from typing import Optional
from pydantic import BaseModel, ConfigDict


class StoreSettingUpdate(BaseModel):
    store_name: Optional[str] = None
    store_branch: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    currency_symbol: Optional[str] = None
    exchange_rate_khr: Optional[float] = None
    tax_rate: Optional[float] = None
    printer_name: Optional[str] = None
    printer_paper_width: Optional[int] = None
    auto_print_receipt: Optional[bool] = None
    sound_alert: Optional[bool] = None
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_alerts_enabled: Optional[bool] = None


class StoreSettingResponse(BaseModel):
    id: int
    store_id: Optional[int] = None
    store_name: str
    store_branch: str
    phone_number: str
    email: str
    address: str
    currency_symbol: str
    exchange_rate_khr: float
    tax_rate: float
    printer_name: str
    printer_paper_width: int
    auto_print_receipt: bool
    sound_alert: bool
    receipt_header: str
    receipt_footer: str
    telegram_alerts_enabled: bool

    model_config = ConfigDict(from_attributes=True)
