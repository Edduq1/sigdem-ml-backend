import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class TramiteEstado(str, enum.Enum):
    REGISTRADO = "REGISTRADO"
    EN_REVISION = "EN_REVISION"
    OBSERVADO = "OBSERVADO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    FINALIZADO = "FINALIZADO"


class TramitePrioridad(str, enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class Tramite(Base):
    __tablename__ = "tramites"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, index=True, nullable=False)

    tipo_tramite = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)

    area_responsable = Column(String(150), nullable=False)
    correo_solicitante = Column(String(150), nullable=True)

    estado = Column(Enum(TramiteEstado), default=TramiteEstado.REGISTRADO, nullable=False)
    prioridad = Column(Enum(TramitePrioridad), default=TramitePrioridad.MEDIA, nullable=False)

    recepcionista_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    analista_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    fecha_registro = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TramiteHistory(Base):
    __tablename__ = "tramite_history"

    id = Column(Integer, primary_key=True, index=True)

    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    accion = Column(String(100), nullable=False)
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=True)
    comentario = Column(Text, nullable=True)

    fecha = Column(DateTime, default=datetime.utcnow)

    tramite = relationship("Tramite")