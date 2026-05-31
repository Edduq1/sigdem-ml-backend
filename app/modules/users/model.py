import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum

from app.database.connection import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    RECEPCIONISTA = "RECEPCIONISTA"
    ANALISTA = "ANALISTA"
    RRHH = "RRHH"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(Enum(UserRole), nullable=False, default=UserRole.RECEPCIONISTA)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)