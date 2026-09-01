from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, desc, case
from app.models.sale import Sale, SaleItem


class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: int, store_id: Optional[int] = None) -> Optional[Sale]:
        query = self.db.query(Sale).options(selectinload(Sale.items)).filter(Sale.id == sale_id)
        if store_id is not None:
            query = query.filter(Sale.store_id == store_id)
        return query.first()

    def get_by_invoice(self, invoice_no: str, store_id: Optional[int] = None) -> Optional[Sale]:
        query = self.db.query(Sale).options(selectinload(Sale.items)).filter(Sale.invoice_no == invoice_no)
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
        query = self.db.query(Sale).options(selectinload(Sale.items)).filter(Sale.store_id == store_id)

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

    def get_sales_metrics(
        self,
        store_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Executes a single SQL query with conditional aggregations to get all sales metrics at once.
        """
        query = self.db.query(
            func.count(Sale.id).label("total_transactions"),
            func.coalesce(func.sum(Sale.total_amount), 0.0).label("income"),
            func.coalesce(
                func.sum(case((Sale.payment_method == "CASH", Sale.total_amount), else_=0.0)), 0.0
            ).label("cash_sales"),
            func.coalesce(
                func.sum(case((Sale.payment_method == "ABA_KHQR", Sale.total_amount), else_=0.0)), 0.0
            ).label("khqr_sales"),
        ).filter(Sale.store_id == store_id)

        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)

        row = query.first()
        if not row:
            return {"total_transactions": 0, "income": 0.0, "cash_sales": 0.0, "khqr_sales": 0.0}

        return {
            "total_transactions": int(row.total_transactions or 0),
            "income": float(row.income or 0.0),
            "cash_sales": float(row.cash_sales or 0.0),
            "khqr_sales": float(row.khqr_sales or 0.0),
        }

    def get_daily_sales_stats(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Tuple[int, float]]:
        """
        Returns a dictionary mapping 'YYYY-MM-DD' -> (transaction_count, total_sales)
        using a single grouped SQL query.
        """
        date_expr = func.date(Sale.created_at)
        rows = (
            self.db.query(
                date_expr.label("sale_date"),
                func.count(Sale.id).label("transactions_count"),
                func.coalesce(func.sum(Sale.total_amount), 0.0).label("total_sales"),
            )
            .filter(
                Sale.store_id == store_id,
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
            )
            .group_by(date_expr)
            .all()
        )

        results: Dict[str, Tuple[int, float]] = {}
        for r in rows:
            d_str = str(r.sale_date) if r.sale_date else ""
            results[d_str] = (int(r.transactions_count or 0), float(r.total_sales or 0.0))
        return results

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

