from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class PaymentInput(BaseModel):
    amount: Decimal | None = Field(None, ge=0)
    currency: str = Field("JPY", max_length=3)
    payment_cycle: str | None = None
    payment_day: int | None = Field(None, ge=1, le=31)
    payment_method: str | None = Field(None, max_length=50)
    is_tax_included: bool = True
    payment_notes: str | None = None


class PaymentResponse(BaseModel):
    amount: str | None
    currency: str
    payment_cycle: str | None
    payment_day: int | None
    payment_method: str | None
    is_tax_included: bool
    payment_notes: str | None

    @field_serializer("amount")
    def serialize_amount(self, value: str | None) -> str | None:
        return value
