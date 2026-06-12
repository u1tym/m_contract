from fastapi import APIRouter, Response, status

from app.deps import CurrentAid, DbSession
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import ItemsResponse
from app.services.contract_service import ContractService

router = APIRouter(prefix="/categories", tags=["categories"])
service = ContractService()


@router.get("", response_model=ItemsResponse[CategoryResponse])
def list_categories(aid: CurrentAid, db: DbSession) -> ItemsResponse[CategoryResponse]:
    items = service.list_categories(db, aid)
    return ItemsResponse(items=items)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(aid: CurrentAid, db: DbSession, data: CategoryCreate) -> CategoryResponse:
    return service.create_category(db, aid, data)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    aid: CurrentAid,
    db: DbSession,
    category_id: int,
    data: CategoryUpdate,
) -> CategoryResponse:
    return service.update_category(db, aid, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(aid: CurrentAid, db: DbSession, category_id: int) -> Response:
    service.delete_category(db, aid, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
