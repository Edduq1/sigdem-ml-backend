from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.ml.cv_schema import (
    CVMatchRequest,
    CVMatchResponse,
    CVRankingResponse
)
from app.modules.ml.cv_service import (
    calculate_cv_job_match,
    generate_cv_ranking
)


router = APIRouter(
    prefix="/api/ml/cv",
    tags=["Machine Learning - CVs"]
)


rrhh_or_admin = RoleChecker([
    UserRole.ADMIN,
    UserRole.RRHH
])


@router.post("/match", response_model=CVMatchResponse)
def match_cv_with_job(
    data: CVMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return calculate_cv_job_match(db, data.cv_id, data.job_id)


@router.get("/ranking/{job_id}", response_model=CVRankingResponse)
def ranking_by_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(rrhh_or_admin)
):
    return generate_cv_ranking(db, job_id)