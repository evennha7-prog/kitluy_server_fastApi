from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_optional_current_user, get_tenant_store_id
from app.models.user import User
from app.schemas.sale import CheckoutRequest, SaleResponse
from app.services.sale_service import SaleService

router = APIRouter(prefix="/sales", tags=["Sales & POS Checkout"])


@router.post("/checkout", response_model=SaleResponse)
def checkout(
    req: CheckoutRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SaleService(db)
    return service.checkout(req, store_id=store_id, cashier_user=current_user)


@router.get("", response_model=List[SaleResponse])
def list_sales(
    filter_preset: Optional[str] = Query(None, description="today, yesterday, this_week"),
    payment_method: Optional[str] = Query(None, description="CASH, ABA_KHQR, CARD"),
    skip: int = 0,
    limit: int = 100,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SaleService(db)
    return service.list_sales(
        store_id=store_id,
        skip=skip,
        limit=limit,
        filter_preset=filter_preset,
        payment_method=payment_method,
    )


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SaleService(db)
    return service.get_sale_by_id(sale_id, store_id=store_id)
