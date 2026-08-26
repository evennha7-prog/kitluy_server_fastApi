from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, supplier_id: int, store_id: Optional[int] = None) -> Optional[Supplier]:
        query = self.db.query(Supplier).filter(Supplier.id == supplier_id)
        if store_id is not None:
            query = query.filter(Supplier.store_id == store_id)
        return query.first()

    def list_suppliers(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        query: Optional[str] = None,
    ) -> List[Supplier]:
        db_query = self.db.query(Supplier).filter(Supplier.store_id == store_id, Supplier.is_active == True)
        if query:
            db_query = db_query.filter(
                or_(
                    Supplier.name.ilike(f"%{query}%"),
                    Supplier.company_name.ilike(f"%{query}%"),
                    Supplier.phone.ilike(f"%{query}%"),
                    Supplier.category.ilike(f"%{query}%"),
                )
            )
        return db_query.offset(skip).limit(limit).all()

    def create(self, supplier: Supplier) -> Supplier:
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def update(self, supplier: Supplier) -> Supplier:
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def delete(self, supplier: Supplier) -> None:
        self.db.delete(supplier)
        self.db.commit()
