from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.auth.routes import get_current_user
from app.modules.users.model import User, UserRole
from app.utils.roles import RoleChecker

from app.modules.tramites.schema import (
    TramiteCreate,
    TramiteUpdate,
    TramiteStatusUpdate,
    TramiteAssignAnalyst,
    TramiteResponse,
    TramiteHistoryResponse
)
from app.modules.tramites.service import (
    create_tramite,
    get_tramites,
    get_tramite_by_id,
    update_tramite,
    change_tramite_status,
    assign_analyst,
    get_tramite_history
)


router = APIRouter(
    prefix="/api/tramites",
    tags=["Trámites"]
)


can_create_tramite = RoleChecker([
    UserRole.ADMIN,
    UserRole.RECEPCIONISTA
])

can_manage_tramite = RoleChecker([
    UserRole.ADMIN,
    UserRole.ANALISTA,
    UserRole.RECEPCIONISTA
])

admin_or_recepcion = RoleChecker([
    UserRole.ADMIN,
    UserRole.RECEPCIONISTA
])


@router.post("/", response_model=TramiteResponse)
def create_new_tramite(
    data: TramiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_create_tramite)
):
    return create_tramite(db, data, current_user)


@router.get("/", response_model=list[TramiteResponse])
def list_tramites(
    estado: str | None = None,
    prioridad: str | None = None,
    area: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_tramites(db, estado, prioridad, area)


@router.get("/{tramite_id}", response_model=TramiteResponse)
def detail_tramite(
    tramite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_tramite_by_id(db, tramite_id)


@router.put("/{tramite_id}", response_model=TramiteResponse)
def edit_tramite(
    tramite_id: int,
    data: TramiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_tramite)
):
    return update_tramite(db, tramite_id, data, current_user)


@router.patch("/{tramite_id}/status", response_model=TramiteResponse)
def update_status(
    tramite_id: int,
    data: TramiteStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_manage_tramite)
):
    return change_tramite_status(db, tramite_id, data, current_user)


@router.patch("/{tramite_id}/assign", response_model=TramiteResponse)
def assign_tramite_analyst(
    tramite_id: int,
    data: TramiteAssignAnalyst,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_recepcion)
):
    return assign_analyst(db, tramite_id, data, current_user)


@router.get("/{tramite_id}/history", response_model=list[TramiteHistoryResponse])
def tramite_history(
    tramite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_tramite_history(db, tramite_id)