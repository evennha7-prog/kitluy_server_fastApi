from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PurchaseItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    quantity: int = 1
    unit_cost: float


class PurchaseItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: str
    quantity: int
    unit_cost: float
    total_cost: float

    model_config = ConfigDict(from_attributes=True)


class PurchaseCreate(BaseModel):
    supplier_id: Optional[int] = None
    supplier_name: str
    invoice_no: Optional[str] = None
    items: List[PurchaseItemCreate]
    note: Optional[str] = None


class PurchaseResponse(BaseModel):
    id: int
    store_id: Optional[int] = None
    supplier_id: Optional[int] = None
    supplier_name: str
    invoice_no: str
    total_amount: float
    status: str
    note: Optional[str] = None
    created_at: datetime
    items: List[PurchaseItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
