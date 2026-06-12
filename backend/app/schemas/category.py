from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    icon: str | None = Field(None, max_length=50)
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    icon: str | None = Field(None, max_length=50)
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str | None
    sort_order: int
