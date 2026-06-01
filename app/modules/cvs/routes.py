from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.cvs.schema import CVResponse, CVExtractResponse
from app.modules.cvs.service import (
    upload_cv,
    get_cvs,
    get_cv_by_id,
    extract_text_from_cv,
    delete_cv,
    download_cv
)


router = APIRouter(
    prefix="/api/cvs",
    tags=["CVs"]
)


rrhh_or_admin = RoleChecker([
    UserRole.ADMIN,
    UserRole.RRHH
])


@router.post("/upload", response_model=CVResponse)
def upload_new_cv(
    file: UploadFile = File(...),
    nombre_candidato: str = Form(...),
    correo_candidato: str | None = Form(None),
    telefono_candidato: str | None = Form(None),
    job_id: int | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return upload_cv(
        db=db,
        file=file,
        current_user=current_user,
        nombre_candidato=nombre_candidato,
        correo_candidato=correo_candidato,
        telefono_candidato=telefono_candidato,
        job_id=job_id
    )


@router.get("/", response_model=list[CVResponse])
def list_cvs(
    job_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return get_cvs(db, job_id)


@router.get("/{cv_id}", response_model=CVResponse)
def detail_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return get_cv_by_id(db, cv_id)


@router.get("/{cv_id}/download")
def download_cv_file(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return download_cv(db, cv_id)


@router.post("/{cv_id}/extract", response_model=CVExtractResponse)
def extract_cv_text(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return extract_text_from_cv(db, cv_id, current_user)


@router.delete("/{cv_id}")
def remove_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return delete_cv(db, cv_id)