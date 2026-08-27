from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class StaffLinkBase(BaseModel):
    role_title: str = "Cashier"  # Cashier, Barista, Inventory, Supervisor
    permissions: Optional[str] = '["pos_sales", "discount"]'
    is_active: bool = True


class StaffLinkCreate(StaffLinkBase):
    full_name: str
    phone_number: str
    password: Optional[str] = "123456"
    email: Optional[str] = None
    pin_code: Optional[str] = "0000"
    shift: Optional[str] = "Morning Shift (06:30 AM - 03:00 PM)"
    avatar_index: int = 0


class StaffLinkUpdate(BaseModel):
    role_title: Optional[str] = None
    permissions: Optional[str] = None
    is_active: Optional[bool] = None
    shift: Optional[str] = None
    pin_code: Optional[str] = None
    avatar_index: Optional[int] = None


class StaffLinkResponse(BaseModel):
    id: int
    store_owner_id: int
    store_id: int
    staff_user_id: int
    role_title: str
    permissions: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # User info
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    pin_code: Optional[str] = None
    shift: Optional[str] = None
    avatar_index: int = 0
    store_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
