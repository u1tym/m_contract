from datetime import date

from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse
from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.credential import CredentialCreate, CredentialResponse
from app.schemas.payment import PaymentInput, PaymentResponse
from app.schemas.attachment import AttachmentResponse


class CategoryBrief(BaseModel):
    id: int
    name: str
    icon: str | None


class ContractCreate(BaseModel):
    category_id: int
    provider_name: str = Field(..., max_length=200)
    contract_name: str | None = Field(None, max_length=200)
    contract_number: str | None = Field(None, max_length=100)
    status: str = "active"
    start_date: date | None = None
    end_date: date | None = None
    renewal_date: date | None = None
    auto_renewal: bool = True
    notes: str | None = None
    payment: PaymentInput | None = None
    credentials: list[CredentialCreate] = Field(default_factory=list)
    contacts: list[ContactCreate] = Field(default_factory=list)


class ContractUpdate(BaseModel):
    category_id: int | None = None
    provider_name: str | None = Field(None, max_length=200)
    contract_name: str | None = Field(None, max_length=200)
    contract_number: str | None = Field(None, max_length=100)
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    renewal_date: date | None = None
    auto_renewal: bool | None = None
    notes: str | None = None
    payment: PaymentInput | None = None


class ContractSummaryResponse(BaseModel):
    id: int
    category: CategoryBrief
    provider_name: str
    contract_name: str | None
    status: str
    start_date: date | None
    end_date: date | None
    amount: str | None
    payment_cycle: str | None
    monthly_amount: str
    credential_count: int
    attachment_count: int
    updated_at: str


class ContractDetailResponse(BaseModel):
    id: int
    category_id: int
    category: CategoryBrief
    provider_name: str
    contract_name: str | None
    contract_number: str | None
    status: str
    start_date: date | None
    end_date: date | None
    renewal_date: date | None
    auto_renewal: bool
    notes: str | None
    payment: PaymentResponse
    credentials: list[CredentialResponse]
    contacts: list[ContactResponse]
    attachments: list[AttachmentResponse]
    created_at: str
    updated_at: str
