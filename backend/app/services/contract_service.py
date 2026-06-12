from __future__ import annotations

import math
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.exceptions import AppError
from app.models import (
    MASKED_CREDENTIAL_TYPES,
    Attachment,
    Category,
    Contact,
    Contract,
    Credential,
)
from app.schemas.attachment import AttachmentResponse, AttachmentUpdate
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import format_datetime_jst
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.schemas.contract import (
    CategoryBrief,
    ContractCreate,
    ContractDetailResponse,
    ContractSummaryResponse,
    ContractUpdate,
)
from app.schemas.credential import (
    CredentialCreate,
    CredentialResponse,
    CredentialRevealResponse,
    CredentialUpdate,
)
from app.schemas.dashboard import CategorySummary, DashboardSummary, UpcomingRenewal
from app.schemas.payment import PaymentInput, PaymentResponse
from app.services.encryption_service import EncryptionService
from app.services.storage_service import StorageService

MASK_VALUE = "********"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _format_amount(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"{value:.2f}"


def calc_monthly_amount(amount: Decimal | None, payment_cycle: str | None) -> Decimal:
    if amount is None or payment_cycle is None:
        return Decimal("0")
    if payment_cycle == "monthly":
        return amount
    if payment_cycle == "yearly":
        return amount / Decimal("12")
    if payment_cycle == "quarterly":
        return amount / Decimal("3")
    if payment_cycle == "biannual":
        return amount / Decimal("6")
    return Decimal("0")


class ContractService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._encryption = EncryptionService(self._settings.secret_key)
        self._storage = StorageService(self._settings)

    def _get_category(self, db: Session, aid: int, category_id: int) -> Category:
        category = db.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.aid == aid,
                Category.is_deleted.is_(False),
            )
        )
        if category is None:
            raise AppError(404, "カテゴリが見つかりません", "NOT_FOUND")
        return category

    def _get_contract(self, db: Session, aid: int, contract_id: int) -> Contract:
        contract = db.scalar(
            select(Contract).where(
                Contract.id == contract_id,
                Contract.aid == aid,
                Contract.is_deleted.is_(False),
            )
        )
        if contract is None:
            raise AppError(404, "契約が見つかりません", "NOT_FOUND")
        return contract

    def _apply_payment(self, contract: Contract, payment: PaymentInput | None) -> None:
        if payment is None:
            return
        contract.amount = payment.amount
        contract.currency = payment.currency
        contract.payment_cycle = payment.payment_cycle
        contract.payment_day = payment.payment_day
        contract.payment_method = payment.payment_method
        contract.is_tax_included = payment.is_tax_included
        contract.payment_notes = payment.payment_notes

    def _payment_response(self, contract: Contract) -> PaymentResponse:
        return PaymentResponse(
            amount=_format_amount(contract.amount),
            currency=contract.currency,
            payment_cycle=contract.payment_cycle,
            payment_day=contract.payment_day,
            payment_method=contract.payment_method,
            is_tax_included=contract.is_tax_included,
            payment_notes=contract.payment_notes,
        )

    def _category_brief(self, category: Category) -> CategoryBrief:
        return CategoryBrief(id=category.id, name=category.name, icon=category.icon)

    def _credential_response(self, row: Credential, *, reveal: bool = False) -> CredentialResponse:
        masked = row.credential_type in MASKED_CREDENTIAL_TYPES and not reveal
        if masked:
            display_value = MASK_VALUE
        else:
            display_value = self._encryption.decrypt(row.value)
        return CredentialResponse(
            id=row.id,
            credential_type=row.credential_type,
            label=row.label,
            value=display_value,
            is_masked=masked,
            url=row.url,
            notes=row.notes,
            sort_order=row.sort_order,
        )

    def _contact_response(self, row: Contact) -> ContactResponse:
        return ContactResponse(
            id=row.id,
            contact_type=row.contact_type,
            label=row.label,
            value=row.value,
            notes=row.notes,
            sort_order=row.sort_order,
        )

    def _attachment_response(self, row: Attachment) -> AttachmentResponse:
        return AttachmentResponse(
            id=row.id,
            file_name=row.file_name,
            content_type=row.content_type,
            file_size=row.file_size,
            description=row.description,
            sort_order=row.sort_order,
            created_at=format_datetime_jst(row.created_at),
        )

    def _contract_detail(self, contract: Contract) -> ContractDetailResponse:
        credentials = [
            self._credential_response(row)
            for row in sorted(contract.credentials, key=lambda c: c.sort_order)
            if not row.is_deleted
        ]
        contacts = [
            self._contact_response(row)
            for row in sorted(contract.contacts, key=lambda c: c.sort_order)
            if not row.is_deleted
        ]
        attachments = [
            self._attachment_response(row)
            for row in sorted(contract.attachments, key=lambda a: a.sort_order)
            if not row.is_deleted
        ]
        return ContractDetailResponse(
            id=contract.id,
            category_id=contract.category_id,
            category=self._category_brief(contract.category),
            provider_name=contract.provider_name,
            contract_name=contract.contract_name,
            contract_number=contract.contract_number,
            status=contract.status,
            start_date=contract.start_date,
            end_date=contract.end_date,
            renewal_date=contract.renewal_date,
            auto_renewal=contract.auto_renewal,
            notes=contract.notes,
            payment=self._payment_response(contract),
            credentials=credentials,
            contacts=contacts,
            attachments=attachments,
            created_at=format_datetime_jst(contract.created_at),
            updated_at=format_datetime_jst(contract.updated_at),
        )

    def list_categories(self, db: Session, aid: int) -> list[CategoryResponse]:
        rows = db.scalars(
            select(Category)
            .where(Category.aid == aid, Category.is_deleted.is_(False))
            .order_by(Category.sort_order, Category.id)
        ).all()
        return [
            CategoryResponse(id=row.id, name=row.name, icon=row.icon, sort_order=row.sort_order)
            for row in rows
        ]

    def create_category(self, db: Session, aid: int, data: CategoryCreate) -> CategoryResponse:
        now = _utc_now()
        row = Category(
            aid=aid,
            name=data.name,
            icon=data.icon,
            sort_order=data.sort_order,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise AppError(409, "同名のカテゴリが既に存在します", "CATEGORY_NAME_DUPLICATE") from exc
        db.refresh(row)
        return CategoryResponse(id=row.id, name=row.name, icon=row.icon, sort_order=row.sort_order)

    def update_category(
        self, db: Session, aid: int, category_id: int, data: CategoryUpdate
    ) -> CategoryResponse:
        row = self._get_category(db, aid, category_id)
        if data.name is not None:
            row.name = data.name
        if data.icon is not None:
            row.icon = data.icon
        if data.sort_order is not None:
            row.sort_order = data.sort_order
        row.updated_at = _utc_now()
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise AppError(409, "同名のカテゴリが既に存在します", "CATEGORY_NAME_DUPLICATE") from exc
        db.refresh(row)
        return CategoryResponse(id=row.id, name=row.name, icon=row.icon, sort_order=row.sort_order)

    def delete_category(self, db: Session, aid: int, category_id: int) -> None:
        row = self._get_category(db, aid, category_id)
        in_use = db.scalar(
            select(func.count())
            .select_from(Contract)
            .where(
                Contract.category_id == category_id,
                Contract.aid == aid,
                Contract.is_deleted.is_(False),
            )
        )
        if in_use and in_use > 0:
            raise AppError(409, "契約が紐づいているため削除できません", "CATEGORY_IN_USE")
        row.is_deleted = True
        row.updated_at = _utc_now()
        db.commit()

    def list_contracts(
        self,
        db: Session,
        aid: int,
        *,
        page: int,
        per_page: int,
        status: str | None,
        category_id: int | None,
        q: str | None,
        sort: str,
    ) -> tuple[list[ContractSummaryResponse], int]:
        query = select(Contract).where(Contract.aid == aid, Contract.is_deleted.is_(False))
        if status:
            query = query.where(Contract.status == status)
        if category_id is not None:
            query = query.where(Contract.category_id == category_id)
        if q:
            pattern = f"%{q}%"
            query = query.where(
                or_(
                    Contract.provider_name.ilike(pattern),
                    Contract.contract_name.ilike(pattern),
                    Contract.contract_number.ilike(pattern),
                )
            )

        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        if sort == "provider_name_asc":
            query = query.order_by(Contract.provider_name.asc(), Contract.id.asc())
        elif sort == "start_date_desc":
            query = query.order_by(Contract.start_date.desc().nullslast(), Contract.id.desc())
        else:
            query = query.order_by(Contract.updated_at.desc(), Contract.id.desc())

        rows = db.scalars(
            query.options(selectinload(Contract.category))
            .offset((page - 1) * per_page)
            .limit(per_page)
        ).all()

        summaries: list[ContractSummaryResponse] = []
        for row in rows:
            cred_count = db.scalar(
                select(func.count())
                .select_from(Credential)
                .where(
                    Credential.contract_id == row.id,
                    Credential.is_deleted.is_(False),
                )
            ) or 0
            attach_count = db.scalar(
                select(func.count())
                .select_from(Attachment)
                .where(
                    Attachment.contract_id == row.id,
                    Attachment.is_deleted.is_(False),
                )
            ) or 0
            monthly = calc_monthly_amount(row.amount, row.payment_cycle)
            summaries.append(
                ContractSummaryResponse(
                    id=row.id,
                    category=self._category_brief(row.category),
                    provider_name=row.provider_name,
                    contract_name=row.contract_name,
                    status=row.status,
                    start_date=row.start_date,
                    end_date=row.end_date,
                    amount=_format_amount(row.amount),
                    payment_cycle=row.payment_cycle,
                    monthly_amount=f"{monthly:.2f}",
                    credential_count=cred_count,
                    attachment_count=attach_count,
                    updated_at=format_datetime_jst(row.updated_at),
                )
            )
        return summaries, total

    def get_contract_detail(self, db: Session, aid: int, contract_id: int) -> ContractDetailResponse:
        contract = db.scalar(
            select(Contract)
            .where(
                Contract.id == contract_id,
                Contract.aid == aid,
                Contract.is_deleted.is_(False),
            )
            .options(
                selectinload(Contract.category),
                selectinload(Contract.credentials),
                selectinload(Contract.contacts),
                selectinload(Contract.attachments),
            )
        )
        if contract is None:
            raise AppError(404, "契約が見つかりません", "NOT_FOUND")
        return self._contract_detail(contract)

    def create_contract(self, db: Session, aid: int, data: ContractCreate) -> ContractDetailResponse:
        category = self._get_category(db, aid, data.category_id)
        now = _utc_now()
        contract = Contract(
            aid=aid,
            category_id=category.id,
            provider_name=data.provider_name,
            contract_name=data.contract_name,
            contract_number=data.contract_number,
            status=data.status,
            start_date=data.start_date,
            end_date=data.end_date,
            renewal_date=data.renewal_date,
            auto_renewal=data.auto_renewal,
            notes=data.notes,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        self._apply_payment(contract, data.payment)
        db.add(contract)
        db.flush()

        for item in data.credentials:
            db.add(
                Credential(
                    contract_id=contract.id,
                    credential_type=item.credential_type,
                    label=item.label,
                    value=self._encryption.encrypt(item.value),
                    url=item.url,
                    notes=item.notes,
                    sort_order=item.sort_order,
                    is_deleted=False,
                    created_at=now,
                    updated_at=now,
                )
            )
        for item in data.contacts:
            db.add(
                Contact(
                    contract_id=contract.id,
                    contact_type=item.contact_type,
                    label=item.label,
                    value=item.value,
                    notes=item.notes,
                    sort_order=item.sort_order,
                    is_deleted=False,
                    created_at=now,
                    updated_at=now,
                )
            )
        db.commit()
        return self.get_contract_detail(db, aid, contract.id)

    def update_contract(
        self, db: Session, aid: int, contract_id: int, data: ContractUpdate
    ) -> ContractDetailResponse:
        contract = self._get_contract(db, aid, contract_id)
        if data.category_id is not None:
            self._get_category(db, aid, data.category_id)
            contract.category_id = data.category_id
        if data.provider_name is not None:
            contract.provider_name = data.provider_name
        if data.contract_name is not None:
            contract.contract_name = data.contract_name
        if data.contract_number is not None:
            contract.contract_number = data.contract_number
        if data.status is not None:
            contract.status = data.status
        if data.start_date is not None:
            contract.start_date = data.start_date
        if data.end_date is not None:
            contract.end_date = data.end_date
        if data.renewal_date is not None:
            contract.renewal_date = data.renewal_date
        if data.auto_renewal is not None:
            contract.auto_renewal = data.auto_renewal
        if data.notes is not None:
            contract.notes = data.notes
        if data.payment is not None:
            self._apply_payment(contract, data.payment)
        contract.updated_at = _utc_now()
        db.commit()
        return self.get_contract_detail(db, aid, contract_id)

    def delete_contract(self, db: Session, aid: int, contract_id: int) -> None:
        contract = db.scalar(
            select(Contract)
            .where(
                Contract.id == contract_id,
                Contract.aid == aid,
                Contract.is_deleted.is_(False),
            )
            .options(
                selectinload(Contract.credentials),
                selectinload(Contract.contacts),
                selectinload(Contract.attachments),
            )
        )
        if contract is None:
            raise AppError(404, "契約が見つかりません", "NOT_FOUND")

        now = _utc_now()
        contract.is_deleted = True
        contract.updated_at = now

        for credential in contract.credentials:
            if not credential.is_deleted:
                credential.is_deleted = True
                credential.updated_at = now
        for contact in contract.contacts:
            if not contact.is_deleted:
                contact.is_deleted = True
                contact.updated_at = now
        for attachment in contract.attachments:
            if not attachment.is_deleted:
                attachment.is_deleted = True
                attachment.updated_at = now
                self._storage.delete_file(attachment.storage_path)

        db.commit()

    def list_credentials(self, db: Session, aid: int, contract_id: int) -> list[CredentialResponse]:
        self._get_contract(db, aid, contract_id)
        rows = db.scalars(
            select(Credential)
            .where(
                Credential.contract_id == contract_id,
                Credential.is_deleted.is_(False),
            )
            .order_by(Credential.sort_order, Credential.id)
        ).all()
        return [self._credential_response(row) for row in rows]

    def create_credential(
        self, db: Session, aid: int, contract_id: int, data: CredentialCreate
    ) -> CredentialResponse:
        self._get_contract(db, aid, contract_id)
        now = _utc_now()
        row = Credential(
            contract_id=contract_id,
            credential_type=data.credential_type,
            label=data.label,
            value=self._encryption.encrypt(data.value),
            url=data.url,
            notes=data.notes,
            sort_order=data.sort_order,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return self._credential_response(row)

    def update_credential(
        self,
        db: Session,
        aid: int,
        contract_id: int,
        credential_id: int,
        data: CredentialUpdate,
    ) -> CredentialResponse:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Credential).where(
                Credential.id == credential_id,
                Credential.contract_id == contract_id,
                Credential.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "認証情報が見つかりません", "NOT_FOUND")

        if data.credential_type is not None:
            row.credential_type = data.credential_type
        if data.label is not None:
            row.label = data.label
        if data.value is not None:
            row.value = self._encryption.encrypt(data.value)
        if data.url is not None:
            row.url = data.url
        if data.notes is not None:
            row.notes = data.notes
        if data.sort_order is not None:
            row.sort_order = data.sort_order
        row.updated_at = _utc_now()
        db.commit()
        db.refresh(row)
        return self._credential_response(row)

    def delete_credential(
        self, db: Session, aid: int, contract_id: int, credential_id: int
    ) -> None:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Credential).where(
                Credential.id == credential_id,
                Credential.contract_id == contract_id,
                Credential.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "認証情報が見つかりません", "NOT_FOUND")
        row.is_deleted = True
        row.updated_at = _utc_now()
        db.commit()

    def reveal_credential(
        self, db: Session, aid: int, contract_id: int, credential_id: int
    ) -> CredentialRevealResponse:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Credential).where(
                Credential.id == credential_id,
                Credential.contract_id == contract_id,
                Credential.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "認証情報が見つかりません", "NOT_FOUND")
        return CredentialRevealResponse(
            id=row.id,
            credential_type=row.credential_type,
            label=row.label,
            value=self._encryption.decrypt(row.value),
        )

    def list_contacts(self, db: Session, aid: int, contract_id: int) -> list[ContactResponse]:
        self._get_contract(db, aid, contract_id)
        rows = db.scalars(
            select(Contact)
            .where(Contact.contract_id == contract_id, Contact.is_deleted.is_(False))
            .order_by(Contact.sort_order, Contact.id)
        ).all()
        return [self._contact_response(row) for row in rows]

    def create_contact(
        self, db: Session, aid: int, contract_id: int, data: ContactCreate
    ) -> ContactResponse:
        self._get_contract(db, aid, contract_id)
        now = _utc_now()
        row = Contact(
            contract_id=contract_id,
            contact_type=data.contact_type,
            label=data.label,
            value=data.value,
            notes=data.notes,
            sort_order=data.sort_order,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return self._contact_response(row)

    def update_contact(
        self, db: Session, aid: int, contract_id: int, contact_id: int, data: ContactUpdate
    ) -> ContactResponse:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Contact).where(
                Contact.id == contact_id,
                Contact.contract_id == contract_id,
                Contact.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "連絡先が見つかりません", "NOT_FOUND")

        if data.contact_type is not None:
            row.contact_type = data.contact_type
        if data.label is not None:
            row.label = data.label
        if data.value is not None:
            row.value = data.value
        if data.notes is not None:
            row.notes = data.notes
        if data.sort_order is not None:
            row.sort_order = data.sort_order
        row.updated_at = _utc_now()
        db.commit()
        db.refresh(row)
        return self._contact_response(row)

    def delete_contact(self, db: Session, aid: int, contract_id: int, contact_id: int) -> None:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Contact).where(
                Contact.id == contact_id,
                Contact.contract_id == contract_id,
                Contact.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "連絡先が見つかりません", "NOT_FOUND")
        row.is_deleted = True
        row.updated_at = _utc_now()
        db.commit()

    def list_attachments(
        self, db: Session, aid: int, contract_id: int
    ) -> list[AttachmentResponse]:
        self._get_contract(db, aid, contract_id)
        rows = db.scalars(
            select(Attachment)
            .where(Attachment.contract_id == contract_id, Attachment.is_deleted.is_(False))
            .order_by(Attachment.sort_order, Attachment.id)
        ).all()
        return [self._attachment_response(row) for row in rows]

    async def create_attachment(
        self,
        db: Session,
        aid: int,
        contract_id: int,
        file: UploadFile,
        description: str | None,
        sort_order: int,
    ) -> AttachmentResponse:
        self._get_contract(db, aid, contract_id)
        content = await file.read()
        self._storage.validate_upload(file, content)
        storage_path = self._storage.save_file(aid, contract_id, file.filename or "file", content)
        now = _utc_now()
        row = Attachment(
            contract_id=contract_id,
            file_name=file.filename or "file",
            storage_path=storage_path,
            content_type=file.content_type,
            file_size=len(content),
            description=description,
            sort_order=sort_order,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return self._attachment_response(row)

    def update_attachment(
        self,
        db: Session,
        aid: int,
        contract_id: int,
        attachment_id: int,
        data: AttachmentUpdate,
    ) -> AttachmentResponse:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Attachment).where(
                Attachment.id == attachment_id,
                Attachment.contract_id == contract_id,
                Attachment.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "ファイルが見つかりません", "NOT_FOUND")
        if data.description is not None:
            row.description = data.description
        if data.sort_order is not None:
            row.sort_order = data.sort_order
        row.updated_at = _utc_now()
        db.commit()
        db.refresh(row)
        return self._attachment_response(row)

    def delete_attachment(
        self, db: Session, aid: int, contract_id: int, attachment_id: int
    ) -> None:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Attachment).where(
                Attachment.id == attachment_id,
                Attachment.contract_id == contract_id,
                Attachment.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "ファイルが見つかりません", "NOT_FOUND")
        self._storage.delete_file(row.storage_path)
        row.is_deleted = True
        row.updated_at = _utc_now()
        db.commit()

    def get_attachment_file(
        self, db: Session, aid: int, contract_id: int, attachment_id: int
    ) -> tuple[Path, str, str]:
        self._get_contract(db, aid, contract_id)
        row = db.scalar(
            select(Attachment).where(
                Attachment.id == attachment_id,
                Attachment.contract_id == contract_id,
                Attachment.is_deleted.is_(False),
            )
        )
        if row is None:
            raise AppError(404, "ファイルが見つかりません", "NOT_FOUND")
        path = self._storage.resolve_path(row.storage_path)
        if not path.exists():
            raise AppError(404, "ファイルが見つかりません", "NOT_FOUND")
        return path, row.file_name, row.content_type or "application/octet-stream"

    def get_dashboard(self, db: Session, aid: int) -> DashboardSummary:
        contracts = db.scalars(
            select(Contract)
            .where(Contract.aid == aid, Contract.is_deleted.is_(False))
            .options(selectinload(Contract.category))
        ).all()

        total_contracts = len(contracts)
        active_contracts = sum(1 for c in contracts if c.status == "active")
        monthly_total = Decimal("0")
        category_map: dict[int, CategorySummary] = {}
        upcoming: list[UpcomingRenewal] = []
        today = date.today()

        for contract in contracts:
            monthly = calc_monthly_amount(contract.amount, contract.payment_cycle)
            if contract.status == "active":
                monthly_total += monthly

            cat_id = contract.category_id
            if cat_id not in category_map:
                category_map[cat_id] = CategorySummary(
                    category_id=cat_id,
                    category_name=contract.category.name,
                    contract_count=0,
                    monthly_amount="0.00",
                )
            summary = category_map[cat_id]
            summary.contract_count += 1
            if contract.status == "active":
                current = Decimal(summary.monthly_amount)
                summary.monthly_amount = f"{current + monthly:.2f}"

            if contract.renewal_date and contract.renewal_date >= today and contract.status == "active":
                upcoming.append(
                    UpcomingRenewal(
                        contract_id=contract.id,
                        provider_name=contract.provider_name,
                        renewal_date=contract.renewal_date,
                    )
                )

        upcoming.sort(key=lambda item: item.renewal_date)
        by_category = sorted(category_map.values(), key=lambda item: item.category_name)

        return DashboardSummary(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            monthly_total_amount=f"{monthly_total:.2f}",
            by_category=by_category,
            upcoming_renewals=upcoming[:10],
        )


def total_pages(total: int, per_page: int) -> int:
    if total == 0:
        return 0
    return math.ceil(total / per_page)
