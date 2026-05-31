from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    tramite_id: int | None
    uploaded_by_id: int | None
    nombre_original: str
    nombre_guardado: str
    tipo_archivo: str
    ruta_archivo: str
    texto_extraido: str | None
    ocr_procesado: str | None
    fecha_subida: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentOCRResponse(BaseModel):
    document_id: int
    texto_extraido: str
    message: str