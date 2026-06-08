from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    correo: EmailStr
    password: str = Field(min_length=6)
    rol: str = "Tecnico"


class UserRead(BaseModel):
    usuario_id: int
    nombre: str
    correo: str
    rol: str
    estado: str
    fecha_registro: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProjectCreate(BaseModel):
    nombre_proyecto: str = Field(min_length=3, max_length=140)
    descripcion: str | None = None
    ciudad: str = "Cuenca"


class ProjectRead(BaseModel):
    proyecto_id: int
    usuario_id: int
    nombre_proyecto: str
    descripcion: str | None
    ciudad: str
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ModelRead(BaseModel):
    modelo_id: int
    nombre_modelo: str
    tipo_entorno: str
    freq_min_mhz: float
    freq_max_mhz: float
    descripcion: str | None

    class Config:
        from_attributes = True


class CoverageRequest(BaseModel):
    proyecto_id: int | None = None
    nombre_proyecto: str = "Simulación rápida"
    ciudad: str = "Cuenca"
    nombre_antena: str = "Antena principal"
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    frecuencia_mhz: float = Field(gt=0)
    potencia_dbm: float = 43.0
    ganancia_dbi: float = 15.0
    radio_km: float = Field(gt=0, le=50)
    resolucion_m: float = Field(default=250.0, ge=50, le=5000)
    threshold_dbm: float = -100.0
    tecnologia: str = "LTE/5G"


class CoverageResponse(BaseModel):
    proyecto_id: int
    antena_id: int
    simulacion_id: int
    resultado_id: int
    resumen: dict
    geojson: dict
