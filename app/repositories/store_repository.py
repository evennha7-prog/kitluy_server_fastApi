from typing import List, Optional, Dict, Any
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

    def count_all(self, is_active: Optional[bool] = None) -> int:
        query = self.db.query(func.count(Store.id))
        if is_active is not None:
            query = query.filter(Store.is_active == is_active)
        return query.scalar() or 0

    def get_store_stats(self, store_id: int) -> Dict[str, Any]:
        total_staff = self.db.query(func.count(User.id)).filter(User.store_id == store_id).scalar() or 0
        total_products = self.db.query(func.count(Product.id)).filter(Product.store_id == store_id, Product.is_active == True).scalar() or 0
        total_sales_count = self.db.query(func.count(Sale.id)).filter(Sale.store_id == store_id).scalar() or 0
        total_revenue = self.db.query(func.coalesce(func.sum(Sale.total_amount), 0.0)).filter(Sale.store_id == store_id).scalar() or 0.0

        return {
            "total_staff": total_staff,
            "total_products": total_products,
            "total_sales_count": total_sales_count,
            "total_revenue": round(float(total_revenue), 2),
        }

    def get_stores_stats_batch(self, store_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Executes 3 grouped queries to calculate stats for all requested store IDs at once.
        Eliminates N+1 query loop when listing multiple stores.
        """
        if not store_ids:
            return {}

        results: Dict[int, Dict[str, Any]] = {
            sid: {
                "total_staff": 0,
                "total_products": 0,
                "total_sales_count": 0,
                "total_revenue": 0.0,
            }
            for sid in store_ids
        }

        # 1. Staff counts per store
        staff_rows = (
            self.db.query(User.store_id, func.count(User.id))
            .filter(User.store_id.in_(store_ids))
            .group_by(User.store_id)
            .all()
        )
        for sid, count in staff_rows:
            if sid in results:
                results[sid]["total_staff"] = int(count or 0)

        # 2. Product counts per store
        prod_rows = (
            self.db.query(Product.store_id, func.count(Product.id))
            .filter(Product.store_id.in_(store_ids), Product.is_active == True)
            .group_by(Product.store_id)
            .all()
        )
        for sid, count in prod_rows:
            if sid in results:
                results[sid]["total_products"] = int(count or 0)

        # 3. Sales count and revenue per store
        sales_rows = (
            self.db.query(
                Sale.store_id,
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total_amount), 0.0),
            )
            .filter(Sale.store_id.in_(store_ids))
            .group_by(Sale.store_id)
            .all()
        )
        for sid, count, rev in sales_rows:
            if sid in results:
                results[sid]["total_sales_count"] = int(count or 0)
                results[sid]["total_revenue"] = round(float(rev or 0.0), 2)

        return results

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

