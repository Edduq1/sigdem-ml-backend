from sqlalchemy.orm import Session
from sqlalchemy import func

from app.modules.users.model import User
from app.modules.tramites.model import Tramite
from app.modules.documents.model import Document
from app.modules.hr.model import Job
from app.modules.cvs.model import CV


def get_dashboard_summary(db: Session):
    return {
        "total_usuarios": db.query(User).count(),
        "total_tramites": db.query(Tramite).count(),
        "total_documentos": db.query(Document).count(),
        "total_convocatorias": db.query(Job).count(),
        "total_cvs": db.query(CV).count()
    }


def get_tramites_by_status(db: Session):
    results = db.query(
        Tramite.estado,
        func.count(Tramite.id)
    ).group_by(Tramite.estado).all()

    return [
        {
            "estado": estado.value if hasattr(estado, "value") else str(estado),
            "total": total
        }
        for estado, total in results
    ]


def get_tramites_by_priority(db: Session):
    results = db.query(
        Tramite.prioridad,
        func.count(Tramite.id)
    ).group_by(Tramite.prioridad).all()

    return [
        {
            "prioridad": prioridad.value if hasattr(prioridad, "value") else str(prioridad),
            "total": total
        }
        for prioridad, total in results
    ]


def get_rrhh_dashboard(db: Session):
    total_cvs = db.query(CV).count()
    cvs_procesados = db.query(CV).filter(CV.texto_procesado == "SI").count()
    cvs_pendientes = db.query(CV).filter(CV.texto_procesado == "NO").count()

    return {
        "total_convocatorias": db.query(Job).count(),
        "total_cvs": total_cvs,
        "cvs_procesados": cvs_procesados,
        "cvs_pendientes": cvs_pendientes
    }