from fastapi import APIRouter, Response, status

from app.deps import CurrentAid, DbSession
from app.schemas.common import ItemsResponse
from app.schemas.credential import (
    CredentialCreate,
    CredentialResponse,
    CredentialRevealResponse,
    CredentialUpdate,
)
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts/{contract_id}/credentials", tags=["credentials"])
service = ContractService()


@router.get("", response_model=ItemsResponse[CredentialResponse])
def list_credentials(
    aid: CurrentAid, db: DbSession, contract_id: int
) -> ItemsResponse[CredentialResponse]:
    items = service.list_credentials(db, aid, contract_id)
    return ItemsResponse(items=items)


@router.post("", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
def create_credential(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    data: CredentialCreate,
) -> CredentialResponse:
    return service.create_credential(db, aid, contract_id, data)


@router.put("/{credential_id}", response_model=CredentialResponse)
def update_credential(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    credential_id: int,
    data: CredentialUpdate,
) -> CredentialResponse:
    return service.update_credential(db, aid, contract_id, credential_id, data)


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credential(
    aid: CurrentAid, db: DbSession, contract_id: int, credential_id: int
) -> Response:
    service.delete_credential(db, aid, contract_id, credential_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{credential_id}/reveal", response_model=CredentialRevealResponse)
def reveal_credential(
    aid: CurrentAid, db: DbSession, contract_id: int, credential_id: int
) -> CredentialRevealResponse:
    return service.reveal_credential(db, aid, contract_id, credential_id)
