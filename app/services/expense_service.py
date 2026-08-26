from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse


class ExpenseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExpenseRepository(db)

    def list_expenses(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        filter_preset: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[ExpenseResponse]:
        now = datetime.now(timezone.utc)
        start_date = None
        end_date = None

        if filter_preset == "today":
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
            end_date = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)
        elif filter_preset == "yesterday":
            y = now - timedelta(days=1)
            start_date = datetime(y.year, y.month, y.day, 0, 0, 0, tzinfo=timezone.utc)
            end_date = datetime(y.year, y.month, y.day, 23, 59, 59, tzinfo=timezone.utc)
        elif filter_preset == "this_week":
            start_of_week = now - timedelta(days=now.weekday())
            start_date = datetime(start_of_week.year, start_of_week.month, start_of_week.day, 0, 0, 0, tzinfo=timezone.utc)
            end_date = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)

        expenses = self.repo.list_expenses(
            store_id=store_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
        return [ExpenseResponse.model_validate(e) for e in expenses]

    def create_expense(self, expense_in: ExpenseCreate, store_id: int, user=None) -> ExpenseResponse:
        recorded_by = user.full_name if user else (expense_in.recorded_by or "Admin")
        expense = Expense(
            store_id=store_id,
            title=expense_in.title,
            category=expense_in.category or "Utilities",
            amount=expense_in.amount,
            date=expense_in.date or datetime.now(timezone.utc),
            note=expense_in.note,
            recorded_by=recorded_by,
        )
        created = self.repo.create(expense)
        return ExpenseResponse.model_validate(created)

    def delete_expense(self, expense_id: int, store_id: int) -> dict:
        expense = self.repo.get_by_id(expense_id, store_id=store_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense record not found")
        self.repo.delete(expense)
        return {"message": "Expense deleted"}
