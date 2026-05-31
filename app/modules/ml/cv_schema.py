from pydantic import BaseModel, EmailStr


class CVMatchRequest(BaseModel):
    cv_id: int
    job_id: int


class CVMatchResponse(BaseModel):
    cv_id: int
    job_id: int
    candidato: str
    convocatoria: str
    compatibilidad: float
    resultado: str


class CVRankingItem(BaseModel):
    cv_id: int
    candidato: str
    correo: EmailStr | None
    telefono: str | None
    compatibilidad: float
    resultado: str


class CVRankingResponse(BaseModel):
    job_id: int
    convocatoria: str
    total_candidatos: int
    ranking: list[CVRankingItem]