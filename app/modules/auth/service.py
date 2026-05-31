from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from datetime import datetime, timezone
from app.modules.auth.model import RevokedToken

from app.config import settings
from app.modules.users.service import get_user_by_email
from app.utils.security import verify_password, create_access_token, create_refresh_token


def authenticate_user(db: Session, correo: str, password: str):
    user = get_user_by_email(db, correo)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user


def generate_auth_tokens(user):
    token_data = {
        "sub": user.correo,
        "rol": user.rol.value,
        "user_id": user.id
    }

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def login_user(db: Session, correo: str, password: str):
    user = authenticate_user(db, correo, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    return generate_auth_tokens(user)


def refresh_access_token(db: Session, refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o expirado"
    )

    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        token_type = payload.get("type")
        correo = payload.get("sub")
        jti = payload.get("jti")

        if is_token_revoked(db, jti):
            raise credentials_exception

        if token_type != "refresh" or correo is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, correo)

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return generate_auth_tokens(user)


def is_token_revoked(db: Session, jti: str | None) -> bool:
    if not jti:
        return True

    token = db.query(RevokedToken).filter(
        RevokedToken.jti == jti
    ).first()

    return token is not None


def revoke_token(db: Session, token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        jti = payload.get("jti")
        token_type = payload.get("type")
        exp = payload.get("exp")

        if not jti or not token_type or not exp:
            return

        existing_token = db.query(RevokedToken).filter(
            RevokedToken.jti == jti
        ).first()

        if existing_token:
            return

        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).replace(tzinfo=None)

        revoked_token = RevokedToken(
            jti=jti,
            token_type=token_type,
            expires_at=expires_at
        )

        db.add(revoked_token)
        db.commit()

    except JWTError:
        return


def logout_user(db: Session, access_token: str, refresh_token: str):
    revoke_token(db, access_token)
    revoke_token(db, refresh_token)

    return {
        "message": "Sesión cerrada correctamente"
    }