from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class CVResponse(BaseModel):
    id: int
    job_id: int | None
    uploaded_by_id: int | None

    nombre_candidato: str
    correo_candidato: EmailStr | None
    telefono_candidato: str | None

    nombre_original: str
    nombre_guardado: str
    tipo_archivo: str
    ruta_archivo: str

    texto_extraido: str | None
    texto_procesado: str | None

    fecha_subida: datetime

    model_config = ConfigDict(from_attributes=True)


class CVExtractResponse(BaseModel):
    cv_id: int
    texto_extraido: str
    message: str