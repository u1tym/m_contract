from datetime import date

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentAid, DbSession
from app.schemas.common import PaginatedResponse
from app.schemas.contract import ContractCreate, ContractDetailResponse, ContractSummaryResponse, ContractUpdate
from app.services.contract_service import ContractService, total_pages

router = APIRouter(prefix="/contracts", tags=["contracts"])
service = ContractService()


@router.get("", response_model=PaginatedResponse[ContractSummaryResponse])
def list_contracts(
    aid: CurrentAid,
    db: DbSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    category_id: int | None = None,
    q: str | None = None,
    sort: str = Query("updated_at_desc"),
    group: str | None = Query(None, pattern="^(active|ended|all)$"),
    as_of_date: date | None = None,
    include_deleted: bool = False,
) -> PaginatedResponse[ContractSummaryResponse]:
    items, total = service.list_contracts(
        db,
        aid,
        page=page,
        per_page=per_page,
        status=status,
        category_id=category_id,
        q=q,
        sort=sort,
        group=group,
        as_of_date=as_of_date,
        include_deleted=include_deleted,
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages(total, per_page),
    )


@router.post("", response_model=ContractDetailResponse, status_code=status.HTTP_201_CREATED)
def create_contract(aid: CurrentAid, db: DbSession, data: ContractCreate) -> ContractDetailResponse:
    return service.create_contract(db, aid, data)


@router.get("/{contract_id}", response_model=ContractDetailResponse)
def get_contract(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    include_deleted: bool = False,
) -> ContractDetailResponse:
    return service.get_contract_detail(db, aid, contract_id, include_deleted=include_deleted)


@router.put("/{contract_id}", response_model=ContractDetailResponse)
def update_contract(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    data: ContractUpdate,
) -> ContractDetailResponse:
    return service.update_contract(db, aid, contract_id, data)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(aid: CurrentAid, db: DbSession, contract_id: int) -> Response:
    service.delete_contract(db, aid, contract_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{contract_id}/restore", response_model=ContractDetailResponse)
def restore_contract(
    aid: CurrentAid, db: DbSession, contract_id: int
) -> ContractDetailResponse:
    return service.restore_contract(db, aid, contract_id)
