from datetime import timedelta
from time import perf_counter
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db, wait_for_database
from . import models, schemas
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from .coverage import coverage_geojson

app = FastAPI(
    title="Radio Coverage Web API",
    description="API para simulación web de cobertura radioeléctrica usando FSPL.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_database(db: Session) -> None:
    if not db.query(models.PropagationModel).filter_by(nombre_modelo="FSPL").first():
        db.add(models.PropagationModel(
            nombre_modelo="FSPL",
            tipo_entorno="Espacio libre",
            freq_min_mhz=1,
            freq_max_mhz=100000,
            descripcion="Modelo Free Space Path Loss. No considera altura, terreno ni obstáculos.",
        ))
    if not db.query(models.User).filter_by(correo="admin@cobertura.local").first():
        db.add(models.User(
            nombre="Administrador Demo",
            correo="admin@cobertura.local",
            hashed_password=get_password_hash("admin123"),
            rol="Administrador",
        ))
    db.commit()


@app.on_event("startup")
def on_startup():
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "coverage-api"}


@app.post("/api/auth/register", response_model=schemas.UserRead, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.correo == user.correo).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    db_user = models.User(
        nombre=user.nombre,
        correo=user.correo,
        hashed_password=get_password_hash(user.password),
        rol=user.rol,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña inválidos")
    access_token = create_access_token(
        subject=user.correo,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.get("/api/models", response_model=list[schemas.ModelRead])
def list_models(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.PropagationModel).all()


@app.post("/api/projects", response_model=schemas.ProjectRead, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_project = models.Project(usuario_id=current_user.usuario_id, **project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/api/projects", response_model=list[schemas.ProjectRead])
def list_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Project).filter(models.Project.usuario_id == current_user.usuario_id).order_by(models.Project.fecha_creacion.desc()).all()


@app.post("/api/coverage/calculate", response_model=schemas.CoverageResponse)
def calculate_coverage(
    request: schemas.CoverageRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    start = perf_counter()
    if request.proyecto_id:
        project = db.query(models.Project).filter(
            models.Project.proyecto_id == request.proyecto_id,
            models.Project.usuario_id == current_user.usuario_id,
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    else:
        project = models.Project(
            usuario_id=current_user.usuario_id,
            nombre_proyecto=request.nombre_proyecto,
            descripcion="Proyecto generado desde el cálculo rápido de cobertura.",
            ciudad=request.ciudad,
        )
        db.add(project)
        db.flush()

    model = db.query(models.PropagationModel).filter_by(nombre_modelo="FSPL").first()
    if not model:
        model = models.PropagationModel(nombre_modelo="FSPL", tipo_entorno="Espacio libre")
        db.add(model)
        db.flush()

    antenna = models.Antenna(
        proyecto_id=project.proyecto_id,
        nombre_antena=request.nombre_antena,
        latitud=request.latitud,
        longitud=request.longitud,
        frecuencia_mhz=request.frecuencia_mhz,
        potencia_dbm=request.potencia_dbm,
        ganancia_dbi=request.ganancia_dbi,
        altura_m=None,
        azimut_grados=None,
        tecnologia=request.tecnologia,
    )
    db.add(antenna)
    db.flush()

    simulation = models.Simulation(
        proyecto_id=project.proyecto_id,
        modelo_id=model.modelo_id,
        nombre_simulacion=f"FSPL {request.nombre_antena}",
        radio_km=request.radio_km,
        resolucion_m=request.resolucion_m,
        threshold_dbm=request.threshold_dbm,
        estado="Ejecutada",
    )
    db.add(simulation)
    db.flush()

    summary, geojson = coverage_geojson(
        lat=request.latitud,
        lon=request.longitud,
        frequency_mhz=request.frecuencia_mhz,
        tx_power_dbm=request.potencia_dbm,
        gain_dbi=request.ganancia_dbi,
        radius_km=request.radio_km,
        threshold_dbm=request.threshold_dbm,
    )
    elapsed = perf_counter() - start
    result = models.Result(
        simulacion_id=simulation.simulacion_id,
        antena_id=antenna.antena_id,
        rsrp_promedio_dbm=summary["rsrp_promedio_dbm"],
        rsrp_min_dbm=summary["rsrp_min_dbm"],
        cobertura_porcentaje=summary["cobertura_porcentaje"],
        tiempo_ejecucion_s=round(elapsed, 4),
        observacion=summary["nota"],
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    summary["tiempo_ejecucion_s"] = round(elapsed, 4)
    return {
        "proyecto_id": project.proyecto_id,
        "antena_id": antenna.antena_id,
        "simulacion_id": simulation.simulacion_id,
        "resultado_id": result.resultado_id,
        "resumen": summary,
        "geojson": geojson,
    }
