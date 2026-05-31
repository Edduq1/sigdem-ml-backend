from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.modules.auth.schema import (
    LoginRequest,
    TokenResponse,
    InitialAdminRequest,
    RefreshTokenRequest,
    LogoutRequest
)
from app.modules.auth.service import login_user, refresh_access_token, logout_user, is_token_revoked

from app.modules.users.model import User, UserRole
from app.modules.users.schema import UserCreate, UserResponse
from app.modules.users.service import get_user_by_email, create_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        correo: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")

        if correo is None or token_type != "access" or is_token_revoked(db, jti):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, correo)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user


@router.post("/register-admin", response_model=UserResponse)
def register_initial_admin(
    data: InitialAdminRequest,
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()

    if total_users > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El administrador inicial ya fue registrado"
        )

    user_data = UserCreate(
        nombre=data.nombre,
        correo=data.correo,
        password=data.password,
        rol=UserRole.ADMIN
    )

    return create_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(db, data.correo, data.password)


@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return refresh_access_token(db, data.refresh_token)


@router.post("/logout")
def logout(
    data: LogoutRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return logout_user(db, token, data.refresh_token)


@router.get("/profile", response_model=UserResponse)
def profile(
    current_user: User = Depends(get_current_user)
):
    return current_user