from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.notifications.schema import NotificationCreate, NotificationResponse
from app.modules.notifications.service import (
    create_notification,
    get_notifications,
    get_notification_by_id,
    resend_notification
)


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


can_manage_notifications = RoleChecker([
    UserRole.ADMIN,
    UserRole.RECEPCIONISTA,
    UserRole.ANALISTA,
    UserRole.RRHH
])


@router.post("/email", response_model=NotificationResponse)
def send_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_notifications)
):
    return create_notification(db, data, current_user)


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    estado: str | None = None,
    tramite_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_notifications)
):
    return get_notifications(db, estado, tramite_id)


@router.get("/{notification_id}", response_model=NotificationResponse)
def detail_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_notifications)
):
    return get_notification_by_id(db, notification_id)


@router.post("/{notification_id}/resend", response_model=NotificationResponse)
def resend_existing_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_notifications)
):
    return resend_notification(db, notification_id)