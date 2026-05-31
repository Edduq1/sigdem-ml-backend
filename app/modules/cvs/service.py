import os
import shutil
from uuid import uuid4

import fitz

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.modules.cvs.model import CV
from app.modules.hr.service import get_job_by_id
from app.modules.users.model import User


UPLOAD_DIR = "uploads/cvs"


def upload_cv(
    db: Session,
    file: UploadFile,
    current_user: User,
    nombre_candidato: str,
    correo_candidato: str | None = None,
    telefono_candidato: str | None = None,
    job_id: int | None = None
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    allowed_extensions = [".pdf", ".txt"]

    original_name = file.filename
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos PDF o TXT para currículos"
        )

    if job_id is not None:
        get_job_by_id(db, job_id)

    saved_name = f"{uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cv = CV(
        job_id=job_id,
        uploaded_by_id=current_user.id,
        nombre_candidato=nombre_candidato,
        correo_candidato=correo_candidato,
        telefono_candidato=telefono_candidato,
        nombre_original=original_name,
        nombre_guardado=saved_name,
        tipo_archivo=file.content_type or "application/octet-stream",
        ruta_archivo=file_path
    )

    db.add(cv)
    db.commit()
    db.refresh(cv)

    return cv


def get_cvs(db: Session, job_id: int | None = None):
    query = db.query(CV)

    if job_id is not None:
        query = query.filter(CV.job_id == job_id)

    return query.order_by(CV.id.desc()).all()


def get_cv_by_id(db: Session, cv_id: int):
    cv = db.query(CV).filter(CV.id == cv_id).first()

    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currículo no encontrado"
        )

    return cv


def extract_text_from_cv(
    db: Session,
    cv_id: int,
    current_user: User
):
    cv = get_cv_by_id(db, cv_id)

    if not os.path.exists(cv.ruta_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo físico del CV no existe en el servidor"
        )

    extension = os.path.splitext(cv.nombre_original)[1].lower()

    texto_extraido = ""

    if extension == ".pdf":
        pdf = fitz.open(cv.ruta_archivo)

        for page in pdf:
            texto_extraido += page.get_text()

        pdf.close()

    elif extension == ".txt":
        with open(cv.ruta_archivo, "r", encoding="utf-8") as file:
            texto_extraido = file.read()

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede extraer texto de archivos PDF o TXT"
        )

    if not texto_extraido.strip():
        texto_extraido = "No se pudo extraer texto del CV. Puede ser un PDF escaneado."

    cv.texto_extraido = texto_extraido
    cv.texto_procesado = "SI"

    db.commit()
    db.refresh(cv)

    return {
        "cv_id": cv.id,
        "texto_extraido": texto_extraido,
        "message": "Texto del CV extraído correctamente"
    }


def delete_cv(db: Session, cv_id: int):
    cv = get_cv_by_id(db, cv_id)

    if os.path.exists(cv.ruta_archivo):
        os.remove(cv.ruta_archivo)

    db.delete(cv)
    db.commit()

    return {
        "message": "Currículo eliminado correctamente"
    }