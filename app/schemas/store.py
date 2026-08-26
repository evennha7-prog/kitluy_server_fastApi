from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class StoreBase(BaseModel):
    store_name: str
    store_branch: Optional[str] = "Main Branch"
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    currency_symbol: Optional[str] = "$"
    exchange_rate_khr: Optional[float] = 4100.0
    logo_url: Optional[str] = None


class StoreCreate(StoreBase):
    store_code: Optional[str] = None  # If not provided, auto-generated (e.g. STORE-001)


class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    store_branch: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    currency_symbol: Optional[str] = None
    exchange_rate_khr: Optional[float] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: int
    store_code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StoreWithStatsResponse(StoreResponse):
    total_staff: int = 0
    total_products: int = 0
    total_sales_count: int = 0
    total_revenue: float = 0.0
