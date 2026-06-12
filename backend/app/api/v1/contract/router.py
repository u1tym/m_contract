from fastapi import APIRouter

from app.api.v1.contract import (
    attachments,
    categories,
    contacts,
    contracts,
    credentials,
    dashboard,
)

router = APIRouter(prefix="/api/v1/contract")
router.include_router(categories.router)
router.include_router(contracts.router)
router.include_router(credentials.router)
router.include_router(contacts.router)
router.include_router(attachments.router)
router.include_router(dashboard.router)
