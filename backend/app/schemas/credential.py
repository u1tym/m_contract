from pydantic import BaseModel, Field


class CredentialCreate(BaseModel):
    credential_type: str = Field(..., max_length=30)
    label: str | None = Field(None, max_length=100)
    value: str
    url: str | None = Field(None, max_length=500)
    notes: str | None = None
    sort_order: int = 0


class CredentialUpdate(BaseModel):
    credential_type: str | None = Field(None, max_length=30)
    label: str | None = Field(None, max_length=100)
    value: str | None = None
    url: str | None = Field(None, max_length=500)
    notes: str | None = None
    sort_order: int | None = None


class CredentialResponse(BaseModel):
    id: int
    credential_type: str
    label: str | None
    value: str
    is_masked: bool = False
    url: str | None
    notes: str | None
    sort_order: int


class CredentialRevealResponse(BaseModel):
    id: int
    credential_type: str
    label: str | None
    value: str
