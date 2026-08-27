from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SaleItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    barcode: Optional[str] = None
    unit_price: float
    quantity: int = 1


class SaleItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: str
    barcode: Optional[str] = None
    unit_price: float
    quantity: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    cashier_name: Optional[str] = "Cashier"
    customer_name: Optional[str] = "General Customer"
    customer_phone: Optional[str] = None
    items: List[SaleItemCreate]
    payment_method: str = "CASH"  # CASH, ABA_KHQR, CARD
    discount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    total_amount: Optional[float] = None
    final_amount: Optional[float] = None
    note: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    store_id: Optional[int] = None
    invoice_no: str
    cashier_id: Optional[int] = None
    cashier_name: str
    customer_id: Optional[int] = None
    customer_name: str
    customer_phone: Optional[str] = None
    subtotal: float
    discount: float
    tax: float
    total_amount: float
    payment_method: str
    payment_status: str
    note: Optional[str] = None
    created_at: datetime
    items: List[SaleItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
