from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.store import Store
from app.models.user import User
from app.models.product import Product
from app.models.sale import Sale


class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, store_id: int) -> Optional[Store]:
        return self.db.query(Store).filter(Store.id == store_id).first()

    def get_by_code(self, store_code: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.store_code == store_code).first()

    def list_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Store]:
        query = self.db.query(Store)
        if is_active is not None:
            query = query.filter(Store.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def count_all(self) -> int:
        return self.db.query(func.count(Store.id)).scalar() or 0

    def get_store_stats(self, store_id: int) -> dict:
        total_staff = self.db.query(func.count(User.id)).filter(User.store_id == store_id).scalar() or 0
        total_products = self.db.query(func.count(Product.id)).filter(Product.store_id == store_id, Product.is_active == True).scalar() or 0
        total_sales_count = self.db.query(func.count(Sale.id)).filter(Sale.store_id == store_id).scalar() or 0
        total_revenue = self.db.query(func.sum(Sale.total_amount)).filter(Sale.store_id == store_id).scalar() or 0.0

        return {
            "total_staff": total_staff,
            "total_products": total_products,
            "total_sales_count": total_sales_count,
            "total_revenue": round(float(total_revenue), 2),
        }

    def create(self, store: Store) -> Store:
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def update(self, store: Store) -> Store:
        self.db.commit()
        self.db.refresh(store)
        return store

    def delete(self, store: Store) -> None:
        self.db.delete(store)
        self.db.commit()
