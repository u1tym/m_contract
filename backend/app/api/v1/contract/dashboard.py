from fastapi import APIRouter

from app.deps import CurrentAid, DbSession
from app.schemas.dashboard import DashboardSummary
from app.services.contract_service import ContractService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
service = ContractService()


@router.get("", response_model=DashboardSummary)
def get_dashboard(aid: CurrentAid, db: DbSession) -> DashboardSummary:
    return service.get_dashboard(db, aid)
