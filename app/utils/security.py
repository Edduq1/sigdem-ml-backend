from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({
        "exp": expire,
        "type": token_type,
        "jti": str(uuid4())
    })

    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    expire_time = expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return create_token(
        data=data,
        expires_delta=expire_time,
        token_type="access"
    )


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    expire_time = expires_delta or timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    return create_token(
        data=data,
        expires_delta=expire_time,
        token_type="refresh"
    )