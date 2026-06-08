from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "usuarios"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(40), default="Tecnico")
    estado: Mapped[str] = mapped_column(String(20), default="Activo")
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    proyectos: Mapped[list["Project"]] = relationship(back_populates="usuario")


class Project(Base):
    __tablename__ = "proyectos"

    proyecto_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.usuario_id"), nullable=False)
    nombre_proyecto: Mapped[str] = mapped_column(String(140), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ciudad: Mapped[str] = mapped_column(String(80), default="Cuenca")
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    estado: Mapped[str] = mapped_column(String(20), default="Activo")

    usuario: Mapped[User] = relationship(back_populates="proyectos")
    antenas: Mapped[list["Antenna"]] = relationship(back_populates="proyecto")
    simulaciones: Mapped[list["Simulation"]] = relationship(back_populates="proyecto")


class PropagationModel(Base):
    __tablename__ = "modelos_propagacion"

    modelo_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_modelo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tipo_entorno: Mapped[str] = mapped_column(String(80), default="Espacio libre")
    freq_min_mhz: Mapped[float] = mapped_column(Float, default=1.0)
    freq_max_mhz: Mapped[float] = mapped_column(Float, default=100000.0)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    simulaciones: Mapped[list["Simulation"]] = relationship(back_populates="modelo")


class Antenna(Base):
    __tablename__ = "antenas"

    antena_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.proyecto_id"), nullable=False)
    nombre_antena: Mapped[str] = mapped_column(String(120), nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    frecuencia_mhz: Mapped[float] = mapped_column(Float, nullable=False)
    potencia_dbm: Mapped[float] = mapped_column(Float, nullable=False)
    ganancia_dbi: Mapped[float] = mapped_column(Float, default=0.0)
    altura_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    azimut_grados: Mapped[float | None] = mapped_column(Float, nullable=True)
    tecnologia: Mapped[str] = mapped_column(String(40), default="LTE/5G")

    proyecto: Mapped[Project] = relationship(back_populates="antenas")
    resultados: Mapped[list["Result"]] = relationship(back_populates="antena")


class Simulation(Base):
    __tablename__ = "simulaciones"

    simulacion_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.proyecto_id"), nullable=False)
    modelo_id: Mapped[int] = mapped_column(ForeignKey("modelos_propagacion.modelo_id"), nullable=False)
    nombre_simulacion: Mapped[str] = mapped_column(String(150), nullable=False)
    radio_km: Mapped[float] = mapped_column(Float, nullable=False)
    resolucion_m: Mapped[float] = mapped_column(Float, default=250.0)
    threshold_dbm: Mapped[float] = mapped_column(Float, default=-100.0)
    fecha_ejecucion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    estado: Mapped[str] = mapped_column(String(30), default="Ejecutada")

    proyecto: Mapped[Project] = relationship(back_populates="simulaciones")
    modelo: Mapped[PropagationModel] = relationship(back_populates="simulaciones")
    resultados: Mapped[list["Result"]] = relationship(back_populates="simulacion")
    exportaciones: Mapped[list["Export"]] = relationship(back_populates="simulacion")


class Result(Base):
    __tablename__ = "resultados"

    resultado_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulacion_id: Mapped[int] = mapped_column(ForeignKey("simulaciones.simulacion_id"), nullable=False)
    antena_id: Mapped[int] = mapped_column(ForeignKey("antenas.antena_id"), nullable=False)
    rsrp_promedio_dbm: Mapped[float] = mapped_column(Float, nullable=False)
    rsrp_min_dbm: Mapped[float] = mapped_column(Float, nullable=False)
    cobertura_porcentaje: Mapped[float] = mapped_column(Float, nullable=False)
    tiempo_ejecucion_s: Mapped[float] = mapped_column(Float, default=0.0)
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)

    simulacion: Mapped[Simulation] = relationship(back_populates="resultados")
    antena: Mapped[Antenna] = relationship(back_populates="resultados")


class Export(Base):
    __tablename__ = "exportaciones"

    exportacion_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulacion_id: Mapped[int] = mapped_column(ForeignKey("simulaciones.simulacion_id"), nullable=False)
    formato: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(180), nullable=False)
    fecha_exportacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)

    simulacion: Mapped[Simulation] = relationship(back_populates="exportaciones")
