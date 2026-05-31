from pydantic import BaseModel


class TramitesReportResponse(BaseModel):
    total_tramites: int
    registrados: int
    en_revision: int
    observados: int
    aprobados: int
    rechazados: int
    finalizados: int
    prioridades: dict


class DocumentsReportResponse(BaseModel):
    total_documentos: int
    documentos_con_ocr: int
    documentos_sin_ocr: int
    documentos_asociados_tramite: int


class RRHHReportResponse(BaseModel):
    total_convocatorias: int
    abiertas: int
    pausadas: int
    cerradas: int
    total_cvs: int
    cvs_procesados: int
    cvs_pendientes: int


class NotificationsReportResponse(BaseModel):
    total_notificaciones: int
    enviadas: int
    fallidas: int
    simuladas: int
    pendientes: int