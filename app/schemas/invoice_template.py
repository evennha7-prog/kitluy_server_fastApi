from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserInvoiceTemplateBase(BaseModel):
    style: Optional[str] = "minimal"
    paper_size: Optional[str] = "80mm"
    store_name: Optional[str] = "KITLUY Coffee & Bakery"
    branch_name: Optional[str] = "Main Branch"
    phone_number: Optional[str] = "097 534 8338 / 012 345 678"
    address: Optional[str] = "#128 St 2004, Phnom Penh"
    vat_tin: Optional[str] = "K001-902345890"
    header_message: Optional[str] = "សូមស្វាគមន៍មកកាន់ហាងយើងខ្ញុំ! Welcome!"
    footer_message: Optional[str] = "ទំនិញទិញរួចមិនអាចប្តូរវិញបានទេ\nThank you & See you again!"
    wifi_info: Optional[str] = "Wi-Fi: KITLUY_GUEST / Pass: 88888888"
    show_logo: Optional[bool] = True
    show_khqr: Optional[bool] = True
    show_barcode: Optional[bool] = True
    show_cashier: Optional[bool] = True
    show_table_num: Optional[bool] = True
    show_exchange_rate: Optional[bool] = True
    show_vat_details: Optional[bool] = True
    show_wifi_info: Optional[bool] = True


class UserInvoiceTemplateUpdate(UserInvoiceTemplateBase):
    pass


class UserInvoiceTemplateResponse(UserInvoiceTemplateBase):
    id: int
    user_id: Optional[int] = None
    store_id: Optional[int] = None
    tenant_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
