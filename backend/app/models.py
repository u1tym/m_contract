from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

CONTRACT_STATUS = ("active", "suspended", "cancelled", "pending")
PAYMENT_CYCLES = ("monthly", "yearly", "quarterly", "biannual", "one_time", "other")
CREDENTIAL_TYPES = (
    "login_id",
    "password",
    "pin",
    "customer_number",
    "email",
    "phone",
    "api_key",
    "other",
)
CONTACT_TYPES = ("phone", "email", "url", "address", "other")
MASKED_CREDENTIAL_TYPES = ("password", "api_key")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    session_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_access: Mapped[datetime] = mapped_column(nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)
    random_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "contract"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aid: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    contracts: Mapped[list["Contract"]] = relationship(back_populates="category")


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = {"schema": "contract"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aid: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contract.categories.id"), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contract_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contract_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    auto_renewal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="JPY")
    payment_cycle: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_day: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_tax_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    payment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    category: Mapped["Category"] = relationship(back_populates="contracts")
    credentials: Mapped[list["Credential"]] = relationship(back_populates="contract")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="contract")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="contract")


class Credential(Base):
    __tablename__ = "credentials"
    __table_args__ = {"schema": "contract"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contract.contracts.id"), nullable=False
    )
    credential_type: Mapped[str] = mapped_column(String(30), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    contract: Mapped["Contract"] = relationship(back_populates="credentials")


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = {"schema": "contract"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contract.contracts.id"), nullable=False
    )
    contact_type: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    contract: Mapped["Contract"] = relationship(back_populates="contacts")


class Attachment(Base):
    __tablename__ = "attachments"
    __table_args__ = {"schema": "contract"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contract.contracts.id"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    contract: Mapped["Contract"] = relationship(back_populates="attachments")
