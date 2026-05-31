from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.modules.notifications.model import NotificationStatus


class NotificationCreate(BaseModel):
    destinatario: EmailStr
    asunto: str
    mensaje: str
    tramite_id: int | None = None


class NotificationResponse(BaseModel):
    id: int
    destinatario: EmailStr
    asunto: str
    mensaje: str
    estado: NotificationStatus
    tramite_id: int | None
    created_by_id: int | None
    fecha_creacion: datetime
    fecha_envio: datetime | None

    model_config = ConfigDict(from_attributes=True)