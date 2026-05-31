from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.hr.schema import JobCreate, JobUpdate, JobResponse
from app.modules.hr.service import (
    create_job,
    get_jobs,
    get_job_by_id,
    update_job,
    delete_job
)


router = APIRouter(
    prefix="/api/hr/jobs",
    tags=["RRHH - Convocatorias"]
)


rrhh_or_admin = RoleChecker([
    UserRole.ADMIN,
    UserRole.RRHH
])


@router.post("/", response_model=JobResponse)
def create_new_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return create_job(db, data, current_user)


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    estado: str | None = None,
    area: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return get_jobs(db, estado, area)


@router.get("/{job_id}", response_model=JobResponse)
def detail_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return get_job_by_id(db, job_id)


@router.put("/{job_id}", response_model=JobResponse)
def edit_job(
    job_id: int,
    data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return update_job(db, job_id, data)


@router.delete("/{job_id}")
def remove_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return delete_job(db, job_id)