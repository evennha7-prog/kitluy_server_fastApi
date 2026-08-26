from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.analytics import DashboardSummaryResponse, DailyTransactionResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Dashboard & Analytics"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return service.get_summary(store_id=store_id)


@router.get("/daily-transactions", response_model=List[DailyTransactionResponse])
def get_daily_transactions(
    days: int = Query(7, ge=1, le=30),
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return service.get_daily_transactions(store_id=store_id, days=days)
