from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class StoreOwnerBase(BaseModel):
    business_type: Optional[str] = "Cafe & Beverage"
    business_license: Optional[str] = None


class StoreOwnerCreate(StoreOwnerBase):
    user_id: int
    store_id: Optional[int] = None
    status: Optional[str] = "approved"


class StoreOwnerRegister(BaseModel):
    full_name: str
    phone_number: str
    password: str
    email: Optional[str] = None
    pin_code: Optional[str] = "1234"
    store_name: str
    store_branch: Optional[str] = "Main Branch"
    address: Optional[str] = None
    business_type: Optional[str] = "Cafe & Beverage"
    business_license: Optional[str] = None


class StoreOwnerApproval(BaseModel):
    approved: bool = True
    rejection_reason: Optional[str] = None


class StoreOwnerUpdate(BaseModel):
    business_type: Optional[str] = None
    business_license: Optional[str] = None
    status: Optional[str] = None
    rejection_reason: Optional[str] = None


class StoreOwnerResponse(BaseModel):
    id: int
    user_id: int
    store_id: Optional[int] = None
    status: str
    business_type: Optional[str] = None
    business_license: Optional[str] = None
    rejection_reason: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Nested info
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    store_name: Optional[str] = None
    store_branch: Optional[str] = None
    staff_count: int = 0

    model_config = ConfigDict(from_attributes=True)
