from pydantic import BaseModel, Field


class AttachmentUpdate(BaseModel):
    description: str | None = Field(None, max_length=200)
    sort_order: int | None = None


class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    content_type: str | None
    file_size: int
    description: str | None
    sort_order: int
    created_at: str
