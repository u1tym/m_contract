from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.contract.router import router as contract_router
from app.config import get_settings
from app.exceptions import AppError, app_error_handler

settings = get_settings()

app = FastAPI(title="Contract API", version="1.0.0")
app.add_exception_handler(AppError, app_error_handler)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(contract_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
