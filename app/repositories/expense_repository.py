from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.expense import Expense


class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, expense_id: int, store_id: Optional[int] = None) -> Optional[Expense]:
        query = self.db.query(Expense).filter(Expense.id == expense_id)
        if store_id is not None:
            query = query.filter(Expense.store_id == store_id)
        return query.first()

    def list_expenses(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> List[Expense]:
        query = self.db.query(Expense).filter(Expense.store_id == store_id)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        if category:
            query = query.filter(Expense.category == category)

        return query.order_by(desc(Expense.date)).offset(skip).limit(limit).all()

    def sum_expenses(
        self,
        store_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> float:
        query = self.db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.store_id == store_id
        )
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        if category:
            query = query.filter(Expense.category == category)

        return float(query.scalar() or 0.0)

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def update(self, expense: Expense) -> Expense:
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete(self, expense: Expense) -> None:
        self.db.delete(expense)
        self.db.commit()
