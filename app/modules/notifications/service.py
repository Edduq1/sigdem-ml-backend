import smtplib
from datetime import datetime
from email.message import EmailMessage

from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import SessionLocal
from app.modules.notifications.model import Notification, NotificationStatus
from app.modules.notifications.schema import NotificationCreate
from app.modules.tramites.model import Tramite
from app.modules.users.model import User


def send_email_notification(destinatario: str, asunto: str, mensaje: str) -> NotificationStatus:
    """
    Envía un correo real usando SMTP.
    Si SMTP no está configurado, retorna SIMULADO.
    Si ocurre error, retorna FALLIDO.
    """

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("SMTP no configurado. Notificación simulada.")
        return NotificationStatus.SIMULADO

    email = EmailMessage()
    email["From"] = settings.SMTP_FROM_EMAIL
    email["To"] = destinatario
    email["Subject"] = asunto
    email.set_content(mensaje)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            int(settings.SMTP_PORT),
            timeout=15
        ) as server:
            server.ehlo()

            if settings.SMTP_USE_TLS:
                server.starttls()
                server.ehlo()

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)

        return NotificationStatus.ENVIADO

    except Exception as e:
        print("ERROR SMTP:", str(e))
        return NotificationStatus.FALLIDO


def validate_tramite_exists(db: Session, tramite_id: int):
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()

    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trámite no encontrado"
        )

    return tramite


def create_notification_background(
    db: Session,
    data: NotificationCreate,
    current_user: User,
    background_tasks: BackgroundTasks
):
    """
    Registra la notificación rápido y envía el correo en segundo plano.
    Esto evita que el frontend se quede cargando esperando al SMTP.
    """

    if data.tramite_id is not None:
        validate_tramite_exists(db, data.tramite_id)

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

    background_tasks.add_task(
        process_notification_delivery,
        notification.id
    )

    return notification


def process_notification_delivery(notification_id: int):
    """
    Tarea en segundo plano.
    Abre una nueva sesión de base de datos porque ya no usa la sesión del request.
    """

    db = SessionLocal()

    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification:
            return

        result_status = send_email_notification(
            destinatario=notification.destinatario,
            asunto=notification.asunto,
            mensaje=notification.mensaje
        )

        notification.estado = result_status
        notification.fecha_envio = datetime.utcnow()

        db.commit()

    except Exception as e:
        print("ERROR EN BACKGROUND NOTIFICATION:", str(e))

        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if notification:
            notification.estado = NotificationStatus.FALLIDO
            notification.fecha_envio = datetime.utcnow()
            db.commit()

    finally:
        db.close()


def create_notification(
    db: Session,
    data: NotificationCreate,
    current_user: User
):
    """
    Mantiene compatibilidad con otros módulos del backend.
    Esta versión sigue enviando el correo de forma directa.
    """

    if data.tramite_id is not None:
        validate_tramite_exists(db, data.tramite_id)

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

    notification.estado = NotificationStatus.PENDIENTE
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