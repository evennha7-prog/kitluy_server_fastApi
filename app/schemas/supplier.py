from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SupplierBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = "Coffee Beans & Dairy"


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    store_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
