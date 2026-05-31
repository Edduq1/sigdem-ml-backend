import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey

from app.database.connection import Base


class NotificationStatus(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    ENVIADO = "ENVIADO"
    FALLIDO = "FALLIDO"
    SIMULADO = "SIMULADO"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    destinatario = Column(String(150), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)

    estado = Column(Enum(NotificationStatus), default=NotificationStatus.PENDIENTE, nullable=False)

    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_envio = Column(DateTime, nullable=True)