from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.hr.model import Job
from app.modules.hr.schema import JobCreate, JobUpdate
from app.modules.users.model import User


def create_job(db: Session, data: JobCreate, current_user: User):
    job = Job(
        titulo=data.titulo,
        descripcion=data.descripcion,
        requisitos=data.requisitos,
        area=data.area,
        modalidad=data.modalidad,
        ubicacion=data.ubicacion,
        created_by_id=current_user.id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_jobs(db: Session, estado: str | None = None, area: str | None = None):
    query = db.query(Job)

    if estado:
        query = query.filter(Job.estado == estado)

    if area:
        query = query.filter(Job.area.ilike(f"%{area}%"))

    return query.order_by(Job.id.desc()).all()


def get_job_by_id(db: Session, job_id: int):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convocatoria no encontrada"
        )

    return job


def update_job(db: Session, job_id: int, data: JobUpdate):
    job = get_job_by_id(db, job_id)

    if data.titulo is not None:
        job.titulo = data.titulo

    if data.descripcion is not None:
        job.descripcion = data.descripcion

    if data.requisitos is not None:
        job.requisitos = data.requisitos

    if data.area is not None:
        job.area = data.area

    if data.modalidad is not None:
        job.modalidad = data.modalidad

    if data.ubicacion is not None:
        job.ubicacion = data.ubicacion

    if data.estado is not None:
        job.estado = data.estado

    db.commit()
    db.refresh(job)

    return job


def delete_job(db: Session, job_id: int):
    job = get_job_by_id(db, job_id)

    db.delete(job)
    db.commit()

    return {
        "message": "Convocatoria eliminada correctamente"
    }