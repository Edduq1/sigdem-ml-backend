from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.auth.routes import get_current_user
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.ml.schema import (
    TramiteMLClassifyRequest,
    TramiteMLClassifyResponse,
    TramiteMLTrainResponse,
    TramiteMLMetricsResponse
)
from app.modules.ml.service import (
    classify_tramite_priority,
    predict_priority_for_existing_tramite,
    train_tramite_priority_model,
    get_tramite_model_metrics
)


router = APIRouter(
    prefix="/api/ml/tramites",
    tags=["Machine Learning - Trámites"]
)


admin_only = RoleChecker([
    UserRole.ADMIN
])


admin_or_analyst = RoleChecker([
    UserRole.ADMIN,
    UserRole.ANALISTA
])


@router.post("/classify", response_model=TramiteMLClassifyResponse)
def classify_priority(
    data: TramiteMLClassifyRequest,
    current_user: User = Depends(admin_or_analyst)
):
    return classify_tramite_priority(data)


@router.post("/{tramite_id}/predict")
def predict_existing_tramite_priority(
    tramite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_analyst)
):
    return predict_priority_for_existing_tramite(db, tramite_id, current_user)


@router.post("/train", response_model=TramiteMLTrainResponse)
def train_model(
    current_user: User = Depends(admin_only)
):
    model_package = train_tramite_priority_model()

    return {
        "message": "Modelo Random Forest entrenado correctamente",
        "accuracy": model_package["accuracy"],
        "total_samples": model_package["total_samples"]
    }


@router.get("/metrics", response_model=TramiteMLMetricsResponse)
def model_metrics(
    current_user: User = Depends(admin_or_analyst)
):
    return get_tramite_model_metrics()