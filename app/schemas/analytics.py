from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TopSellingProduct(BaseModel):
    product_name: str
    quantity_sold: int
    total_sales: float


class DashboardSummaryResponse(BaseModel):
    income: float
    expense: float
    net_profit: float
    total_transactions: int
    total_products: int
    total_customers: int
    cash_sales: float
    khqr_sales: float
    top_selling_products: List[TopSellingProduct] = []


class DailyTransactionResponse(BaseModel):
    date: str
    transactions_count: int
    total_sales: float
