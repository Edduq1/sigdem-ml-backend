import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from sqlalchemy.orm import Session

from app.modules.tramites.model import Tramite, TramiteEstado, TramitePrioridad
from app.modules.documents.model import Document
from app.modules.hr.model import Job, JobStatus
from app.modules.cvs.model import CV
from app.modules.notifications.model import Notification, NotificationStatus


def get_tramites_report(db: Session):
    prioridades = {}

    for prioridad in TramitePrioridad:
        prioridades[prioridad.value] = db.query(Tramite).filter(
            Tramite.prioridad == prioridad
        ).count()

    return {
        "total_tramites": db.query(Tramite).count(),
        "registrados": db.query(Tramite).filter(Tramite.estado == TramiteEstado.REGISTRADO).count(),
        "en_revision": db.query(Tramite).filter(Tramite.estado == TramiteEstado.EN_REVISION).count(),
        "observados": db.query(Tramite).filter(Tramite.estado == TramiteEstado.OBSERVADO).count(),
        "aprobados": db.query(Tramite).filter(Tramite.estado == TramiteEstado.APROBADO).count(),
        "rechazados": db.query(Tramite).filter(Tramite.estado == TramiteEstado.RECHAZADO).count(),
        "finalizados": db.query(Tramite).filter(Tramite.estado == TramiteEstado.FINALIZADO).count(),
        "prioridades": prioridades
    }


def get_documents_report(db: Session):
    return {
        "total_documentos": db.query(Document).count(),
        "documentos_con_ocr": db.query(Document).filter(Document.ocr_procesado == "SI").count(),
        "documentos_sin_ocr": db.query(Document).filter(Document.ocr_procesado == "NO").count(),
        "documentos_asociados_tramite": db.query(Document).filter(Document.tramite_id.isnot(None)).count()
    }


def get_rrhh_report(db: Session):
    return {
        "total_convocatorias": db.query(Job).count(),
        "abiertas": db.query(Job).filter(Job.estado == JobStatus.ABIERTA).count(),
        "pausadas": db.query(Job).filter(Job.estado == JobStatus.PAUSADA).count(),
        "cerradas": db.query(Job).filter(Job.estado == JobStatus.CERRADA).count(),
        "total_cvs": db.query(CV).count(),
        "cvs_procesados": db.query(CV).filter(CV.texto_procesado == "SI").count(),
        "cvs_pendientes": db.query(CV).filter(CV.texto_procesado == "NO").count()
    }


def get_notifications_report(db: Session):
    return {
        "total_notificaciones": db.query(Notification).count(),
        "enviadas": db.query(Notification).filter(Notification.estado == NotificationStatus.ENVIADO).count(),
        "fallidas": db.query(Notification).filter(Notification.estado == NotificationStatus.FALLIDO).count(),
        "simuladas": db.query(Notification).filter(Notification.estado == NotificationStatus.SIMULADO).count(),
        "pendientes": db.query(Notification).filter(Notification.estado == NotificationStatus.PENDIENTE).count()
    }


REPORTS_DIR = "uploads/reports"


def ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def create_basic_pdf(title: str, data: dict, filename: str):
    ensure_reports_dir()

    file_path = os.path.join(REPORTS_DIR, filename)

    pdf = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(2 * cm, y, title)

    y -= 1 * cm

    pdf.setFont("Helvetica", 10)
    pdf.drawString(2 * cm, y, f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    y -= 1.2 * cm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(2 * cm, y, "Resumen del reporte")

    y -= 0.8 * cm

    pdf.setFont("Helvetica", 11)

    for key, value in data.items():
        if y < 2 * cm:
            pdf.showPage()
            y = height - 2 * cm
            pdf.setFont("Helvetica", 11)

        if isinstance(value, dict):
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(2 * cm, y, f"{key}:")
            y -= 0.6 * cm

            pdf.setFont("Helvetica", 11)
            for sub_key, sub_value in value.items():
                pdf.drawString(2.7 * cm, y, f"- {sub_key}: {sub_value}")
                y -= 0.6 * cm
        else:
            pdf.drawString(2 * cm, y, f"{key}: {value}")
            y -= 0.6 * cm

    pdf.save()

    return file_path


def generate_tramites_report_pdf(db: Session):
    data = get_tramites_report(db)

    return create_basic_pdf(
        title="Reporte de Trámites - SIGDEM-ML",
        data=data,
        filename="reporte_tramites.pdf"
    )


def generate_documents_report_pdf(db: Session):
    data = get_documents_report(db)

    return create_basic_pdf(
        title="Reporte Documental - SIGDEM-ML",
        data=data,
        filename="reporte_documentos.pdf"
    )


def generate_rrhh_report_pdf(db: Session):
    data = get_rrhh_report(db)

    return create_basic_pdf(
        title="Reporte RRHH - SIGDEM-ML",
        data=data,
        filename="reporte_rrhh.pdf"
    )


def generate_notifications_report_pdf(db: Session):
    data = get_notifications_report(db)

    return create_basic_pdf(
        title="Reporte de Notificaciones - SIGDEM-ML",
        data=data,
        filename="reporte_notificaciones.pdf"
    )