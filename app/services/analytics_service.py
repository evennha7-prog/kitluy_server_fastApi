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

        # Today's sales (Income)
        income = self.sale_repo.sum_sales(store_id=store_id, start_date=today_start, end_date=today_end)
        cash_sales = self.sale_repo.sum_sales(store_id=store_id, start_date=today_start, end_date=today_end, payment_method="CASH")
        khqr_sales = self.sale_repo.sum_sales(store_id=store_id, start_date=today_start, end_date=today_end, payment_method="ABA_KHQR")

        # Today's expenses
        expense = self.expense_repo.sum_expenses(store_id=store_id, start_date=today_start, end_date=today_end)

        # Total transactions
        total_transactions = self.sale_repo.count_sales(store_id=store_id, start_date=today_start, end_date=today_end)

        # If zero transactions today, provide lifetime totals for dashboard metrics
        if total_transactions == 0:
            income = self.sale_repo.sum_sales(store_id=store_id)
            expense = self.expense_repo.sum_expenses(store_id=store_id)
            total_transactions = self.sale_repo.count_sales(store_id=store_id)
            cash_sales = self.sale_repo.sum_sales(store_id=store_id, payment_method="CASH")
            khqr_sales = self.sale_repo.sum_sales(store_id=store_id, payment_method="ABA_KHQR")

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
        results = []

        for i in range(days - 1, -1, -1):
            day = now - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=timezone.utc)
            day_end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)

            count = self.sale_repo.count_sales(store_id=store_id, start_date=day_start, end_date=day_end)
            sales_sum = self.sale_repo.sum_sales(store_id=store_id, start_date=day_start, end_date=day_end)

            results.append(
                DailyTransactionResponse(
                    date=day.strftime("%Y-%m-%d"),
                    transactions_count=count,
                    total_sales=round(sales_sum, 2),
                )
            )

        return results
