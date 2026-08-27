from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[str] = None
    role: str = "store_admin"  # Default: store_admin (Store Owner), super_admin, cashier, stock_admin
    shift: Optional[str] = "Store Manager (Full-Time)"
    telegram_username: Optional[str] = None
    avatar_index: int = 0
    store_id: Optional[int] = None


class UserCreate(UserBase):
    password: str
    pin_code: Optional[str] = None
    store_name: Optional[str] = None
    store_branch: Optional[str] = "Main Branch"
    business_type: Optional[str] = "Cafe & Beverage"
    address: Optional[str] = None


class StaffCreate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[str] = None
    password: str
    pin_code: Optional[str] = None
    role: str = "cashier"  # cashier, stock_admin, store_admin
    shift: Optional[str] = "Morning Shift (06:30 AM - 03:00 PM)"
    telegram_username: Optional[str] = None
    avatar_index: int = 0


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    shift: Optional[str] = None
    telegram_username: Optional[str] = None
    avatar_index: Optional[int] = None
    is_active: Optional[bool] = None
    pin_code: Optional[str] = None
    store_id: Optional[int] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    shift: Optional[str] = None
    telegram_username: Optional[str] = None
    avatar_index: Optional[int] = None



class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    store_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
