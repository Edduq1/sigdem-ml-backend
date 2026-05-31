import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey

from app.database.connection import Base


class JobStatus(str, enum.Enum):
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    PAUSADA = "PAUSADA"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    requisitos = Column(Text, nullable=False)

    area = Column(String(150), nullable=False)
    modalidad = Column(String(100), nullable=True)
    ubicacion = Column(String(150), nullable=True)

    estado = Column(Enum(JobStatus), default=JobStatus.ABIERTA, nullable=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)