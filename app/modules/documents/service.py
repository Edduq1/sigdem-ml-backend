import os
import shutil
from uuid import uuid4

import fitz

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.modules.documents.model import Document
from app.modules.tramites.service import get_tramite_by_id, create_history
from app.modules.users.model import User


UPLOAD_DIR = "uploads/documents"


def upload_document(
    db: Session,
    file: UploadFile,
    current_user: User,
    tramite_id: int | None = None
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt"]

    original_name = file.filename
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido"
        )

    if tramite_id is not None:
        get_tramite_by_id(db, tramite_id)

    saved_name = f"{uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        tramite_id=tramite_id,
        uploaded_by_id=current_user.id,
        nombre_original=original_name,
        nombre_guardado=saved_name,
        tipo_archivo=file.content_type or "application/octet-stream",
        ruta_archivo=file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    if tramite_id is not None:
        create_history(
            db=db,
            tramite_id=tramite_id,
            usuario_id=current_user.id,
            accion="DOCUMENTO_ADJUNTADO",
            comentario=f"Documento adjuntado: {original_name}"
        )

    return document


def get_documents(db: Session, tramite_id: int | None = None):
    query = db.query(Document)

    if tramite_id is not None:
        query = query.filter(Document.tramite_id == tramite_id)

    return query.order_by(Document.id.desc()).all()


def get_document_by_id(db: Session, document_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )

    return document


def delete_document(db: Session, document_id: int, current_user: User):
    document = get_document_by_id(db, document_id)

    if os.path.exists(document.ruta_archivo):
        os.remove(document.ruta_archivo)

    db.delete(document)
    db.commit()

    return {
        "message": "Documento eliminado correctamente"
    }


def extract_text_from_document(
    db: Session,
    document_id: int,
    current_user: User
):
    document = get_document_by_id(db, document_id)

    if not os.path.exists(document.ruta_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo físico no existe en el servidor"
        )

    extension = os.path.splitext(document.nombre_original)[1].lower()

    texto_extraido = ""

    if extension == ".pdf":
        pdf = fitz.open(document.ruta_archivo)

        for page in pdf:
            texto_extraido += page.get_text()

        pdf.close()

    elif extension in [".txt"]:
        with open(document.ruta_archivo, "r", encoding="utf-8") as file:
            texto_extraido = file.read()

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Por ahora solo se puede extraer texto de archivos PDF o TXT"
        )

    if not texto_extraido.strip():
        texto_extraido = "No se pudo extraer texto del documento. Puede ser un PDF escaneado o una imagen."

    document.texto_extraido = texto_extraido
    document.ocr_procesado = "SI"

    db.commit()
    db.refresh(document)

    if document.tramite_id is not None:
        create_history(
            db=db,
            tramite_id=document.tramite_id,
            usuario_id=current_user.id,
            accion="OCR_DOCUMENTO_PROCESADO",
            comentario=f"Texto extraído del documento: {document.nombre_original}"
        )

    return {
        "document_id": document.id,
        "texto_extraido": texto_extraido,
        "message": "Texto extraído correctamente"
    }