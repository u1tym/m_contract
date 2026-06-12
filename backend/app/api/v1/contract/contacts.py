from fastapi import APIRouter, Response, status

from app.deps import CurrentAid, DbSession
from app.schemas.common import ItemsResponse
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts/{contract_id}/contacts", tags=["contacts"])
service = ContractService()


@router.get("", response_model=ItemsResponse[ContactResponse])
def list_contacts(aid: CurrentAid, db: DbSession, contract_id: int) -> ItemsResponse[ContactResponse]:
    items = service.list_contacts(db, aid, contract_id)
    return ItemsResponse(items=items)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    data: ContactCreate,
) -> ContactResponse:
    return service.create_contact(db, aid, contract_id, data)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    contact_id: int,
    data: ContactUpdate,
) -> ContactResponse:
    return service.update_contact(db, aid, contract_id, contact_id, data)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    aid: CurrentAid, db: DbSession, contract_id: int, contact_id: int
) -> Response:
    service.delete_contact(db, aid, contract_id, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
