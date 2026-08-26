from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    store_id: Optional[int] = None
    store_name: Optional[str] = None
    user: "UserResponse"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    store_id: Optional[int] = None


class LoginRequest(BaseModel):
    identifier: str  # phone or email
    password: str


class PinLoginRequest(BaseModel):
    pin: str  # 4-digit PIN
    store_id: Optional[int] = None  # Optional: specify store for multi-store PIN resolution


class StoreRegisterRequest(BaseModel):
    # Store Details
    store_name: str
    store_branch: Optional[str] = "Main Branch"
    store_code: Optional[str] = None
    address: Optional[str] = None
    currency_symbol: Optional[str] = "$"
    exchange_rate_khr: Optional[float] = 4100.0

    # Admin Details
    admin_name: str
    phone_number: str
    email: Optional[str] = None
    password: str
    pin_code: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    current_pin: Optional[str] = None
    new_pin: Optional[str] = None


from app.schemas.user import UserResponse
Token.model_rebuild()
