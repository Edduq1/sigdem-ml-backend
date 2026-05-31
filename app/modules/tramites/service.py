from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.modules.tramites.model import (
    Tramite,
    TramiteHistory,
    TramiteEstado
)
from app.modules.tramites.schema import (
    TramiteCreate,
    TramiteUpdate,
    TramiteStatusUpdate,
    TramiteAssignAnalyst
)
from app.modules.users.model import User


def generate_tramite_code(db: Session) -> str:
    total = db.query(Tramite).count() + 1
    return f"TRM-{total:06d}"


def create_history(
    db: Session,
    tramite_id: int,
    usuario_id: int | None,
    accion: str,
    estado_anterior: str | None = None,
    estado_nuevo: str | None = None,
    comentario: str | None = None
):
    history = TramiteHistory(
        tramite_id=tramite_id,
        usuario_id=usuario_id,
        accion=accion,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        comentario=comentario
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def create_tramite(db: Session, data: TramiteCreate, current_user: User):
    codigo = generate_tramite_code(db)

    tramite = Tramite(
        codigo=codigo,
        tipo_tramite=data.tipo_tramite,
        descripcion=data.descripcion,
        area_responsable=data.area_responsable,
        correo_solicitante=data.correo_solicitante,
        recepcionista_id=current_user.id
    )

    db.add(tramite)
    db.commit()
    db.refresh(tramite)

    create_history(
        db=db,
        tramite_id=tramite.id,
        usuario_id=current_user.id,
        accion="TRAMITE_REGISTRADO",
        estado_nuevo=tramite.estado.value,
        comentario="Trámite registrado en el sistema"
    )

    return tramite


def get_tramites(
    db: Session,
    estado: str | None = None,
    prioridad: str | None = None,
    area: str | None = None
):
    query = db.query(Tramite)

    if estado:
        query = query.filter(Tramite.estado == estado)

    if prioridad:
        query = query.filter(Tramite.prioridad == prioridad)

    if area:
        query = query.filter(Tramite.area_responsable.ilike(f"%{area}%"))

    return query.order_by(Tramite.id.desc()).all()


def get_tramite_by_id(db: Session, tramite_id: int):
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()

    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trámite no encontrado"
        )

    return tramite


def update_tramite(
    db: Session,
    tramite_id: int,
    data: TramiteUpdate,
    current_user: User
):
    tramite = get_tramite_by_id(db, tramite_id)

    if data.tipo_tramite is not None:
        tramite.tipo_tramite = data.tipo_tramite

    if data.descripcion is not None:
        tramite.descripcion = data.descripcion

    if data.area_responsable is not None:
        tramite.area_responsable = data.area_responsable

    if data.correo_solicitante is not None:
        tramite.correo_solicitante = data.correo_solicitante

    if data.prioridad is not None:
        tramite.prioridad = data.prioridad

    db.commit()
    db.refresh(tramite)

    create_history(
        db=db,
        tramite_id=tramite.id,
        usuario_id=current_user.id,
        accion="TRAMITE_ACTUALIZADO",
        comentario="Datos del trámite actualizados"
    )

    return tramite


def change_tramite_status(
    db: Session,
    tramite_id: int,
    data: TramiteStatusUpdate,
    current_user: User
):
    tramite = get_tramite_by_id(db, tramite_id)

    if tramite.estado == data.estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El trámite ya se encuentra en estado {data.estado.value}"
        )

    estado_anterior = tramite.estado.value
    tramite.estado = data.estado

    db.commit()
    db.refresh(tramite)

    create_history(
        db=db,
        tramite_id=tramite.id,
        usuario_id=current_user.id,
        accion="CAMBIO_ESTADO",
        estado_anterior=estado_anterior,
        estado_nuevo=data.estado.value,
        comentario=data.comentario
    )

    if tramite.correo_solicitante:
        from app.modules.notifications.schema import NotificationCreate
        from app.modules.notifications.service import create_notification

        notification_data = NotificationCreate(
            destinatario=tramite.correo_solicitante,
            asunto=f"Actualización de trámite {tramite.codigo}",
            mensaje=(
                f"Estimado ciudadano,\n\n"
                f"Su trámite con código {tramite.codigo} ha cambiado de estado.\n\n"
                f"Estado anterior: {estado_anterior}\n"
                f"Estado actual: {data.estado.value}\n\n"
                f"Comentario: {data.comentario or 'Sin comentario adicional.'}\n\n"
                f"Municipalidad Provincial de Yau\n"
                f"Sistema SIGDEM-ML"
            ),
            tramite_id=tramite.id
        )

        create_notification(
            db=db,
            data=notification_data,
            current_user=current_user
        )

        create_history(
            db=db,
            tramite_id=tramite.id,
            usuario_id=current_user.id,
            accion="NOTIFICACION_AUTOMATICA_ENVIADA",
            comentario=f"Se notificó automáticamente al correo {tramite.correo_solicitante}"
        )

    return tramite


def assign_analyst(
    db: Session,
    tramite_id: int,
    data: TramiteAssignAnalyst,
    current_user: User
):
    tramite = get_tramite_by_id(db, tramite_id)

    analyst = db.query(User).filter(User.id == data.analista_id).first()

    if not analyst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El analista indicado no existe"
        )

    if analyst.rol.value != "ANALISTA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario seleccionado no tiene rol de ANALISTA"
        )

    if not analyst.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El analista seleccionado se encuentra inactivo"
        )

    estado_anterior = tramite.estado.value

    tramite.analista_id = analyst.id
    tramite.estado = TramiteEstado.EN_REVISION

    db.commit()
    db.refresh(tramite)

    create_history(
        db=db,
        tramite_id=tramite.id,
        usuario_id=current_user.id,
        accion="ANALISTA_ASIGNADO",
        estado_anterior=estado_anterior,
        estado_nuevo=TramiteEstado.EN_REVISION.value,
        comentario=data.comentario or f"Trámite asignado al analista {analyst.nombre}"
    )

    return tramite


def get_tramite_history(db: Session, tramite_id: int):
    get_tramite_by_id(db, tramite_id)

    return db.query(TramiteHistory).filter(
        TramiteHistory.tramite_id == tramite_id
    ).order_by(TramiteHistory.fecha.desc()).all()