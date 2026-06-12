from fastapi import APIRouter, File, Form, Response, UploadFile, status
from fastapi.responses import FileResponse

from app.deps import CurrentAid, DbSession
from app.schemas.attachment import AttachmentResponse, AttachmentUpdate
from app.schemas.common import ItemsResponse
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts/{contract_id}/attachments", tags=["attachments"])
service = ContractService()


@router.get("", response_model=ItemsResponse[AttachmentResponse])
def list_attachments(
    aid: CurrentAid, db: DbSession, contract_id: int
) -> ItemsResponse[AttachmentResponse]:
    items = service.list_attachments(db, aid, contract_id)
    return ItemsResponse(items=items)


@router.post("", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def create_attachment(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    file: UploadFile = File(...),
    description: str | None = Form(None),
    sort_order: int = Form(0),
) -> AttachmentResponse:
    return await service.create_attachment(db, aid, contract_id, file, description, sort_order)


@router.put("/{attachment_id}", response_model=AttachmentResponse)
def update_attachment(
    aid: CurrentAid,
    db: DbSession,
    contract_id: int,
    attachment_id: int,
    data: AttachmentUpdate,
) -> AttachmentResponse:
    return service.update_attachment(db, aid, contract_id, attachment_id, data)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    aid: CurrentAid, db: DbSession, contract_id: int, attachment_id: int
) -> Response:
    service.delete_attachment(db, aid, contract_id, attachment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{attachment_id}/download")
def download_attachment(
    aid: CurrentAid, db: DbSession, contract_id: int, attachment_id: int
) -> FileResponse:
    path, file_name, content_type = service.get_attachment_file(db, aid, contract_id, attachment_id)
    return FileResponse(
        path=path,
        media_type=content_type,
        filename=file_name,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
