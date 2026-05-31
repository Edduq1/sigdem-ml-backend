import smtplib
from datetime import datetime
from email.message import EmailMessage

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.modules.notifications.model import Notification, NotificationStatus
from app.modules.notifications.schema import NotificationCreate
from app.modules.tramites.service import get_tramite_by_id
from app.modules.users.model import User


def send_email_notification(destinatario: str, asunto: str, mensaje: str) -> NotificationStatus:
    """
    Envía un correo real si SMTP está configurado.
    Si no hay SMTP, retorna SIMULADO para pruebas académicas.
    """

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return NotificationStatus.SIMULADO

    email = EmailMessage()
    email["From"] = settings.SMTP_FROM_EMAIL
    email["To"] = destinatario
    email["Subject"] = asunto
    email.set_content(mensaje)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)

        return NotificationStatus.ENVIADO

    except Exception:
        return NotificationStatus.FALLIDO


def create_notification(
    db: Session,
    data: NotificationCreate,
    current_user: User
):
    if data.tramite_id is not None:
        get_tramite_by_id(db, data.tramite_id)

    notification = Notification(
        destinatario=data.destinatario,
        asunto=data.asunto,
        mensaje=data.mensaje,
        tramite_id=data.tramite_id,
        created_by_id=current_user.id,
        estado=NotificationStatus.PENDIENTE
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    result_status = send_email_notification(
        destinatario=notification.destinatario,
        asunto=notification.asunto,
        mensaje=notification.mensaje
    )

    notification.estado = result_status
    notification.fecha_envio = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


def get_notifications(
    db: Session,
    estado: str | None = None,
    tramite_id: int | None = None
):
    query = db.query(Notification)

    if estado:
        query = query.filter(Notification.estado == estado)

    if tramite_id is not None:
        query = query.filter(Notification.tramite_id == tramite_id)

    return query.order_by(Notification.id.desc()).all()


def get_notification_by_id(db: Session, notification_id: int):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )

    return notification


def resend_notification(db: Session, notification_id: int):
    notification = get_notification_by_id(db, notification_id)

    result_status = send_email_notification(
        destinatario=notification.destinatario,
        asunto=notification.asunto,
        mensaje=notification.mensaje
    )

    notification.estado = result_status
    notification.fecha_envio = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification