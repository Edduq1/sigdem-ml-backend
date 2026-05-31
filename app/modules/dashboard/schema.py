from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_usuarios: int
    total_tramites: int
    total_documentos: int
    total_convocatorias: int
    total_cvs: int


class TramitesByStatusResponse(BaseModel):
    estado: str
    total: int


class TramitesByPriorityResponse(BaseModel):
    prioridad: str
    total: int


class DashboardRRHHResponse(BaseModel):
    total_convocatorias: int
    total_cvs: int
    cvs_procesados: int
    cvs_pendientes: int