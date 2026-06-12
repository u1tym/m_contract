from datetime import datetime, timedelta, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

JST = timezone(timedelta(hours=9))
UTC = timezone.utc
T = TypeVar("T")


def format_datetime_jst(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(JST).isoformat(timespec="seconds")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int


class ItemsResponse(BaseModel, Generic[T]):
    items: list[T]


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
