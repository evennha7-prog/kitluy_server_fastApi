from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExpenseBase(BaseModel):
    title: str
    category: str = "Utilities"
    amount: float
    date: Optional[datetime] = None
    note: Optional[str] = None
    recorded_by: Optional[str] = "Admin"


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    note: Optional[str] = None
    recorded_by: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int
    store_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
