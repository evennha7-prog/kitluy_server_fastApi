from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.analytics import DashboardSummaryResponse, DailyTransactionResponse, TopSellingProduct


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.sale_repo = SaleRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)

    def get_summary(self, store_id: int) -> DashboardSummaryResponse:
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
        today_end = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)

        # 1. Single combined query for today's sales metrics
        metrics = self.sale_repo.get_sales_metrics(
            store_id=store_id, start_date=today_start, end_date=today_end
        )
        total_transactions = metrics["total_transactions"]
        income = metrics["income"]
        cash_sales = metrics["cash_sales"]
        khqr_sales = metrics["khqr_sales"]

        # Today's expenses
        expense = self.expense_repo.sum_expenses(store_id=store_id, start_date=today_start, end_date=today_end)

        # If zero transactions today, provide lifetime totals for dashboard metrics
        if total_transactions == 0:
            lifetime_metrics = self.sale_repo.get_sales_metrics(store_id=store_id)
            total_transactions = lifetime_metrics["total_transactions"]
            income = lifetime_metrics["income"]
            cash_sales = lifetime_metrics["cash_sales"]
            khqr_sales = lifetime_metrics["khqr_sales"]
            expense = self.expense_repo.sum_expenses(store_id=store_id)

        net_profit = max(0.0, income - expense)

        # Top selling items
        top_items_data = self.sale_repo.get_top_selling_items(store_id=store_id, limit=5)
        top_selling = [
            TopSellingProduct(
                product_name=item[0],
                quantity_sold=int(item[1]),
                total_sales=round(float(item[2]), 2),
            )
            for item in top_items_data
        ]

        return DashboardSummaryResponse(
            income=round(income, 2),
            expense=round(expense, 2),
            net_profit=round(net_profit, 2),
            total_transactions=total_transactions,
            total_products=self.product_repo.count_products(store_id=store_id),
            total_customers=self.customer_repo.count_customers(store_id=store_id),
            cash_sales=round(cash_sales, 2),
            khqr_sales=round(khqr_sales, 2),
            top_selling_products=top_selling,
        )

    def get_daily_transactions(self, store_id: int, days: int = 7) -> List[DailyTransactionResponse]:
        now = datetime.now(timezone.utc)
        start_date = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc) - timedelta(days=days - 1)
        end_date = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)

        # Single grouped SQL query for the entire date range
        daily_stats_map = self.sale_repo.get_daily_sales_stats(
            store_id=store_id, start_date=start_date, end_date=end_date
        )

        results: List[DailyTransactionResponse] = []
        for i in range(days - 1, -1, -1):
            day = now - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            count, sales_sum = daily_stats_map.get(day_str, (0, 0.0))

            results.append(
                DailyTransactionResponse(
                    date=day_str,
                    transactions_count=count,
                    total_sales=round(sales_sum, 2),
                )
            )

        return results

