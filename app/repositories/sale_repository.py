from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.sale import Sale, SaleItem


class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: int, store_id: Optional[int] = None) -> Optional[Sale]:
        query = self.db.query(Sale).filter(Sale.id == sale_id)
        if store_id is not None:
            query = query.filter(Sale.store_id == store_id)
        return query.first()

    def get_by_invoice(self, invoice_no: str, store_id: Optional[int] = None) -> Optional[Sale]:
        query = self.db.query(Sale).filter(Sale.invoice_no == invoice_no)
        if store_id is not None:
            query = query.filter(Sale.store_id == store_id)
        return query.first()

    def list_sales(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
    ) -> List[Sale]:
        query = self.db.query(Sale).filter(Sale.store_id == store_id)

        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
        if payment_method:
            query = query.filter(Sale.payment_method == payment_method)

        return query.order_by(desc(Sale.created_at)).offset(skip).limit(limit).all()

    def sum_sales(
        self,
        store_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
    ) -> float:
        query = self.db.query(func.coalesce(func.sum(Sale.total_amount), 0.0)).filter(
            Sale.store_id == store_id, Sale.payment_status == "PAID"
        )
        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
        if payment_method:
            query = query.filter(Sale.payment_method == payment_method)
        return float(query.scalar() or 0.0)

    def count_sales(
        self,
        store_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        query = self.db.query(func.count(Sale.id)).filter(Sale.store_id == store_id)
        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
        return int(query.scalar() or 0)

    def get_top_selling_items(self, store_id: int, limit: int = 5) -> List[Tuple[str, int, float]]:
        return (
            self.db.query(
                SaleItem.product_name,
                func.sum(SaleItem.quantity).label("total_qty"),
                func.sum(SaleItem.total_price).label("total_sales"),
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.store_id == store_id)
            .group_by(SaleItem.product_name)
            .order_by(desc("total_qty"))
            .limit(limit)
            .all()
        )

    def create(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale
