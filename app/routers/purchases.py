from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases & Stock-In"])


@router.get("", response_model=List[PurchaseResponse])
def list_purchases(
    skip: int = 0,
    limit: int = 100,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = PurchaseService(db)
    return service.list_purchases(store_id=store_id, skip=skip, limit=limit)


@router.post("", response_model=PurchaseResponse)
def create_purchase(
    purchase_in: PurchaseCreate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = PurchaseService(db)
    return service.create_purchase(purchase_in, store_id=store_id)
