from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.dashboard.schema import (
    DashboardSummaryResponse,
    TramitesByStatusResponse,
    TramitesByPriorityResponse,
    DashboardRRHHResponse
)
from app.modules.dashboard.service import (
    get_dashboard_summary,
    get_tramites_by_status,
    get_tramites_by_priority,
    get_rrhh_dashboard
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
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


@router.get("/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    return get_dashboard_summary(db)


@router.get("/tramites/status", response_model=list[TramitesByStatusResponse])
def tramites_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_analyst)
):
    return get_tramites_by_status(db)


@router.get("/tramites/priorities", response_model=list[TramitesByPriorityResponse])
def tramites_priorities(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_analyst)
):
    return get_tramites_by_priority(db)


@router.get("/rrhh", response_model=DashboardRRHHResponse)
def rrhh_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_rrhh)
):
    return get_rrhh_dashboard(db)