from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    id: int
    store_id: Optional[int] = None
    name: str
    phone: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    points: int = 0
    total_orders: int = 0
    visits_count: Optional[int] = None
    total_spent: float = 0.0
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
