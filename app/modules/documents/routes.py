from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.auth.routes import get_current_user
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.documents.schema import DocumentResponse, DocumentOCRResponse
from app.modules.documents.service import (
    upload_document,
    get_documents,
    get_document_by_id,
    delete_document,
    extract_text_from_document
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


can_manage_documents = RoleChecker([
    UserRole.ADMIN,
    UserRole.RECEPCIONISTA,
    UserRole.ANALISTA
])


@router.post("/upload", response_model=DocumentResponse)
def upload_new_document(
    file: UploadFile = File(...),
    tramite_id: int | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_documents)
):
    return upload_document(db, file, current_user, tramite_id)


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    tramite_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_documents(db, tramite_id)


@router.get("/{document_id}", response_model=DocumentResponse)
def detail_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_document_by_id(db, document_id)


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = get_document_by_id(db, document_id)

    return FileResponse(
        path=document.ruta_archivo,
        filename=document.nombre_original,
        media_type=document.tipo_archivo
    )


@router.post("/{document_id}/ocr", response_model=DocumentOCRResponse)
def process_document_ocr(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_documents)
):
    return extract_text_from_document(db, document_id, current_user)


@router.delete("/{document_id}")
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_documents)
):
    return delete_document(db, document_id, current_user)