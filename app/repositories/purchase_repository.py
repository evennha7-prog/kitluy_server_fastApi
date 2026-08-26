from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.purchase import Purchase


class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, purchase_id: int, store_id: Optional[int] = None) -> Optional[Purchase]:
        query = self.db.query(Purchase).filter(Purchase.id == purchase_id)
        if store_id is not None:
            query = query.filter(Purchase.store_id == store_id)
        return query.first()

    def list_purchases(self, store_id: int, skip: int = 0, limit: int = 100) -> List[Purchase]:
        return (
            self.db.query(Purchase)
            .filter(Purchase.store_id == store_id)
            .order_by(desc(Purchase.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, purchase: Purchase) -> Purchase:
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        return purchase
