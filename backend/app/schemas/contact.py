from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    contact_type: str = Field(..., max_length=20)
    label: str | None = Field(None, max_length=100)
    value: str = Field(..., max_length=500)
    notes: str | None = None
    sort_order: int = 0


class ContactUpdate(BaseModel):
    contact_type: str | None = Field(None, max_length=20)
    label: str | None = Field(None, max_length=100)
    value: str | None = Field(None, max_length=500)
    notes: str | None = None
    sort_order: int | None = None


class ContactResponse(BaseModel):
    id: int
    contact_type: str
    label: str | None
    value: str
    notes: str | None
    sort_order: int
