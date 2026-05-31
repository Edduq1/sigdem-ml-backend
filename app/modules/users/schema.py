from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.modules.users.model import UserRole


class UserCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    rol: UserRole


class UserUpdate(BaseModel):
    nombre: str | None = None
    correo: EmailStr | None = None
    rol: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)