from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_optional_current_user, get_tenant_store_id
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=List[ExpenseResponse])
def list_expenses(
    filter_preset: Optional[str] = Query(None, description="today, yesterday, this_week"),
    category: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ExpenseService(db)
    return service.list_expenses(store_id=store_id, skip=skip, limit=limit, filter_preset=filter_preset, category=category)


@router.post("", response_model=ExpenseResponse)
def create_expense(
    expense_in: ExpenseCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ExpenseService(db)
    return service.create_expense(expense_in, store_id=store_id, user=current_user)


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ExpenseService(db)
    return service.delete_expense(expense_id, store_id=store_id)
