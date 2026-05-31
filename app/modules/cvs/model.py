from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    nombre_candidato = Column(String(150), nullable=False)
    correo_candidato = Column(String(150), nullable=True)
    telefono_candidato = Column(String(50), nullable=True)

    nombre_original = Column(String(255), nullable=False)
    nombre_guardado = Column(String(255), nullable=False)
    tipo_archivo = Column(String(100), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)

    texto_extraido = Column(Text, nullable=True)
    texto_procesado = Column(String(10), default="NO")

    fecha_subida = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job")