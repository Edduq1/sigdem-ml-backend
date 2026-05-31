from pydantic import BaseModel, EmailStr

from app.modules.users.model import UserRole


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class InitialAdminRequest(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    rol: UserRole = UserRole.ADMIN