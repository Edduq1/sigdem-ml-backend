from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker
from fastapi.responses import FileResponse

from app.modules.reports.schema import (
    TramitesReportResponse,
    DocumentsReportResponse,
    RRHHReportResponse,
    NotificationsReportResponse
)
from app.modules.reports.service import (
    get_tramites_report,
    get_documents_report,
    get_rrhh_report,
    get_notifications_report,
    generate_tramites_report_pdf,
    generate_documents_report_pdf,
    generate_rrhh_report_pdf,
    generate_notifications_report_pdf
)


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


admin_only = RoleChecker([
    UserRole.ADMIN
])


admin_or_analyst = RoleChecker([
    UserRole.ADMIN,
    UserRole.ANALISTA
])


admin_or_rrhh = RoleChecker([
    UserRole.ADMIN,
    UserRole.RRHH
])


@router.get("/tramites", response_model=TramitesReportResponse)
def report_tramites(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_analyst)
):
    return get_tramites_report(db)


@router.get("/documents", response_model=DocumentsReportResponse)
def report_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    return get_documents_report(db)


@router.get("/rrhh", response_model=RRHHReportResponse)
def report_rrhh(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_rrhh)
):
    return get_rrhh_report(db)


@router.get("/notifications", response_model=NotificationsReportResponse)
def report_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    return get_notifications_report(db)


@router.get("/tramites/pdf")
def report_tramites_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_analyst)
):
    file_path = generate_tramites_report_pdf(db)

    return FileResponse(
        path=file_path,
        filename="reporte_tramites.pdf",
        media_type="application/pdf"
    )


@router.get("/documents/pdf")
def report_documents_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    file_path = generate_documents_report_pdf(db)

    return FileResponse(
        path=file_path,
        filename="reporte_documentos.pdf",
        media_type="application/pdf"
    )


@router.get("/rrhh/pdf")
def report_rrhh_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_rrhh)
):
    file_path = generate_rrhh_report_pdf(db)

    return FileResponse(
        path=file_path,
        filename="reporte_rrhh.pdf",
        media_type="application/pdf"
    )


@router.get("/notifications/pdf")
def report_notifications_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    file_path = generate_notifications_report_pdf(db)

    return FileResponse(
        path=file_path,
        filename="reporte_notificaciones.pdf",
        media_type="application/pdf"
    )