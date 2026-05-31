from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.modules.users.schema import UserCreate, UserUpdate, UserResponse
from app.modules.users.service import (
    get_users,
    get_user_by_id,
    create_user,
    update_user,
    deactivate_user,
    activate_user,
    delete_user
)
from app.utils.roles import RoleChecker


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


admin_only = RoleChecker([UserRole.ADMIN])


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(admin_only)
):
    return get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def detail_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_only)
):
    return get_user_by_id(db, user_id)


@router.post("/", response_model=UserResponse)
def create_new_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_only)
):
    return create_user(db, data)


@router.put("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_only)
):
    return update_user(db, user_id, data)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    return deactivate_user(db, user_id, current_user)


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    return activate_user(db, user_id)


@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_only)
):
    return delete_user(db, user_id)