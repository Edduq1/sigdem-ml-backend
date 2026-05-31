from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    nombre_original = Column(String(255), nullable=False)
    nombre_guardado = Column(String(255), nullable=False)
    tipo_archivo = Column(String(100), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)

    texto_extraido = Column(Text, nullable=True)
    ocr_procesado = Column(String(10), default="NO")

    fecha_subida = Column(DateTime, default=datetime.utcnow)

    tramite = relationship("Tramite")