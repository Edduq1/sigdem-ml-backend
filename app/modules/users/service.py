from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate
from app.utils.security import hash_password


def get_users(db: Session):
    return db.query(User).order_by(User.id.desc()).all()


def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return user


def get_user_by_email(db: Session, correo: str):
    return db.query(User).filter(User.correo == correo).first()


def create_user(db: Session, data: UserCreate):
    existing_user = get_user_by_email(db, data.correo)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    new_user = User(
        nombre=data.nombre,
        correo=data.correo,
        hashed_password=hash_password(data.password),
        rol=data.rol
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)

    if data.nombre is not None:
        user.nombre = data.nombre

    if data.correo is not None:
        user.correo = data.correo

    if data.rol is not None:
        user.rol = data.rol

    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)

    db.delete(user)
    db.commit()

    return {"message": "Usuario eliminado correctamente"}


def deactivate_user(db: Session, user_id: int, current_user: User):
    user = get_user_by_id(db, user_id)

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propio usuario"
        )

    if user.rol.value == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede desactivar un usuario administrador"
        )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return user


def activate_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)

    user.is_active = True

    db.commit()
    db.refresh(user)

    return user