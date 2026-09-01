from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from app.repositories.purchase_repository import PurchaseRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.purchase import PurchaseCreate, PurchaseResponse


class PurchaseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PurchaseRepository(db)
        self.product_repo = ProductRepository(db)

    def _generate_invoice_no(self) -> str:
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"PO-{today_str}-{datetime.now().microsecond % 10000:04d}"

    def list_purchases(self, store_id: int, skip: int = 0, limit: int = 100) -> List[PurchaseResponse]:
        purchases = self.repo.list_purchases(store_id=store_id, skip=skip, limit=limit)
        return [PurchaseResponse.model_validate(p) for p in purchases]

    def create_purchase(self, purchase_in: PurchaseCreate, store_id: int) -> PurchaseResponse:
        if not purchase_in.items:
            raise HTTPException(status_code=400, detail="Cannot create purchase without items")

        product_ids = [item.product_id for item in purchase_in.items if item.product_id]
        products_map = {p.id: p for p in self.product_repo.get_by_ids(product_ids, store_id=store_id)} if product_ids else {}

        total_amount = 0.0
        purchase_items = []

        for item in purchase_in.items:
            item_total = item.quantity * item.unit_cost
            total_amount += item_total
            purchase_items.append(
                PurchaseItem(
                    store_id=store_id,
                    tenant_id=store_id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_cost=item.unit_cost,
                    total_cost=item_total,
                )
            )

            # Restock product in memory if product_id is specified
            if item.product_id and item.product_id in products_map:
                product = products_map[item.product_id]
                product.stock_qty = (product.stock_qty or 0) + item.quantity
                product.cost_price = item.unit_cost

        invoice_no = purchase_in.invoice_no or self._generate_invoice_no()

        purchase = Purchase(
            store_id=store_id,
            tenant_id=store_id,
            supplier_id=purchase_in.supplier_id,
            supplier_name=purchase_in.supplier_name,
            invoice_no=invoice_no,
            total_amount=round(total_amount, 2),
            status="RECEIVED",
            note=purchase_in.note,
            items=purchase_items,
        )

        created = self.repo.create(purchase)
        return PurchaseResponse.model_validate(created)

