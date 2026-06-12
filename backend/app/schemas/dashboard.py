from datetime import date

from pydantic import BaseModel


class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    contract_count: int
    monthly_amount: str


class UpcomingRenewal(BaseModel):
    contract_id: int
    provider_name: str
    renewal_date: date


class DashboardSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    monthly_total_amount: str
    by_category: list[CategorySummary]
    upcoming_renewals: list[UpcomingRenewal]
