from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.tramites.model import Tramite, TramiteHistory
from app.modules.tramites.routes import router as tramites_router
from app.modules.ml.routes import router as ml_tramites_router

from app.modules.reports.routes import router as reports_router
from app.modules.notifications.model import Notification
from app.modules.notifications.routes import router as notifications_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.ml.cv_routes import router as ml_cv_router
from app.modules.cvs.model import CV
from app.modules.cvs.routes import router as cvs_router
from app.modules.hr.model import Job
from app.modules.hr.routes import router as hr_router
from app.modules.documents.model import Document
from app.modules.documents.routes import router as documents_router
from app.database.connection import Base, engine
from app.modules.auth.model import RevokedToken
from app.modules.users.model import User
from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SIGDEM-ML API",
    description="Backend del Sistema Inteligente de Gestión Documental, Expedientes y Selección de Personal mediante Machine Learning",
    version="1.0.0"
)


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",

    # Frontend desplegado
    "https://sigdem-ml-frontend.vercel.app",

    # Otros dominios futuros:
    # "https://sigdem-ml.netlify.app",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router) 
app.include_router(tramites_router)
app.include_router(ml_tramites_router)
app.include_router(documents_router)
app.include_router(hr_router)
app.include_router(cvs_router)
app.include_router(ml_cv_router)
app.include_router(dashboard_router)
app.include_router(notifications_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "SIGDEM-ML Backend funcionando correctamente"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "SIGDEM-ML API"
    }