from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.modules.tramites.model import TramiteEstado, TramitePrioridad


class TramiteCreate(BaseModel):
    tipo_tramite: str
    descripcion: str
    area_responsable: str
    correo_solicitante: EmailStr | None = None


class TramiteUpdate(BaseModel):
    tipo_tramite: str | None = None
    descripcion: str | None = None
    area_responsable: str | None = None
    correo_solicitante: EmailStr | None = None
    prioridad: TramitePrioridad | None = None


class TramiteStatusUpdate(BaseModel):
    estado: TramiteEstado
    comentario: str | None = None


class TramiteAssignAnalyst(BaseModel):
    analista_id: int
    comentario: str | None = None


class TramiteResponse(BaseModel):
    id: int
    codigo: str
    tipo_tramite: str
    descripcion: str
    area_responsable: str
    correo_solicitante: EmailStr | None
    estado: TramiteEstado
    prioridad: TramitePrioridad
    recepcionista_id: int | None
    analista_id: int | None
    fecha_registro: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


class TramiteHistoryResponse(BaseModel):
    id: int
    tramite_id: int
    usuario_id: int | None
    accion: str
    estado_anterior: str | None
    estado_nuevo: str | None
    comentario: str | None
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)