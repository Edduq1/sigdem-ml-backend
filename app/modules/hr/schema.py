from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.modules.hr.model import JobStatus


class JobCreate(BaseModel):
    titulo: str
    descripcion: str
    requisitos: str
    area: str
    modalidad: str | None = None
    ubicacion: str | None = None


class JobUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    requisitos: str | None = None
    area: str | None = None
    modalidad: str | None = None
    ubicacion: str | None = None
    estado: JobStatus | None = None


class JobResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    requisitos: str
    area: str
    modalidad: str | None
    ubicacion: str | None
    estado: JobStatus
    created_by_id: int | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)