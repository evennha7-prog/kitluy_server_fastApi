from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.customer import Customer
from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.sale import CheckoutRequest, SaleResponse


class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.sale_repo = SaleRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)

    def _generate_invoice_no(self, store_id: int) -> str:
        now_utc = datetime.now(timezone.utc)
        today_str = now_utc.strftime("%Y%m%d")
        time_part = now_utc.strftime("%H%M%S")
        ms_part = f"{now_utc.microsecond // 1000:03d}"
        return f"INV-{today_str}-{time_part}{ms_part[-2:]}"

    def checkout(self, req: CheckoutRequest, store_id: int, cashier_user=None) -> SaleResponse:
        if not req.items:
            raise HTTPException(status_code=400, detail="Cannot checkout an empty cart")

        # 1. Batch fetch products to avoid N+1 queries during checkout
        product_ids = [item.product_id for item in req.items if item.product_id]
        barcodes = [item.barcode for item in req.items if item.barcode and not item.product_id]

        prods_by_id = {p.id: p for p in self.product_repo.get_by_ids(product_ids, store_id=store_id)} if product_ids else {}
        prods_by_bc = {p.barcode: p for p in self.product_repo.get_by_barcodes(barcodes, store_id=store_id)} if barcodes else {}

        subtotal = 0.0
        sale_items = []

        for item_in in req.items:
            product = None
            if item_in.product_id and item_in.product_id in prods_by_id:
                product = prods_by_id[item_in.product_id]
            elif item_in.barcode and item_in.barcode in prods_by_bc:
                product = prods_by_bc[item_in.barcode]

            unit_price = item_in.unit_price
            if product and product.stock_qty is not None:
                product.stock_qty = max(0, product.stock_qty - item_in.quantity)

            item_total = unit_price * item_in.quantity
            subtotal += item_total

            sale_items.append(
                SaleItem(
                    store_id=store_id,
                    tenant_id=store_id,
                    product_id=product.id if product else None,
                    product_name=item_in.product_name,
                    barcode=item_in.barcode or (product.barcode if product else None),
                    unit_price=unit_price,
                    quantity=item_in.quantity,
                    total_price=item_total,
                )
            )

        discount = req.discount or req.discount_amount or 0.0
        tax = req.tax or req.tax_amount or 0.0
        total_amount = max(0.0, subtotal - discount + tax)

        # Customer association
        customer_id = None
        customer_name = req.customer_name or "General Customer"
        if req.customer_phone:
            customer = self.customer_repo.get_by_phone(req.customer_phone, store_id=store_id)
            if customer:
                customer_id = customer.id
                customer.total_orders = (customer.total_orders or 0) + 1
                customer.total_spent = (customer.total_spent or 0.0) + total_amount
                customer.points = (customer.points or 0) + int(total_amount)

        cashier_id = cashier_user.id if cashier_user else None
        cashier_name = cashier_user.full_name if cashier_user else (req.cashier_name or "Cashier")

        sale = Sale(
            store_id=store_id,
            tenant_id=store_id,
            invoice_no=self._generate_invoice_no(store_id=store_id),
            cashier_id=cashier_id,
            cashier_name=cashier_name,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=req.customer_phone,
            subtotal=round(subtotal, 2),
            discount=round(discount, 2),
            tax=round(tax, 2),
            total_amount=round(total_amount, 2),
            payment_method=req.payment_method.upper(),
            payment_status="PAID",
            note=req.note,
            items=sale_items,
        )

        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return SaleResponse.model_validate(sale)


    def list_sales(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        filter_preset: Optional[str] = None,  # today, yesterday, this_week
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
    ) -> List[SaleResponse]:
        now = datetime.now(timezone.utc)

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

        sales = self.sale_repo.list_sales(
            store_id=store_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
        )
        return [SaleResponse.model_validate(s) for s in sales]

    def get_sale_by_id(self, sale_id: int, store_id: Optional[int] = None) -> SaleResponse:
        sale = self.sale_repo.get_by_id(sale_id, store_id=store_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return SaleResponse.model_validate(sale)
