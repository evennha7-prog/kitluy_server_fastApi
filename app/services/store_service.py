import random
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.store import Store
from app.models.setting import StoreSetting
from app.models.product import Category
from app.repositories.store_repository import StoreRepository
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreWithStatsResponse


class StoreService:
    def __init__(self, db: Session):
        self.db = db
        self.store_repo = StoreRepository(db)

    def _generate_store_code(self) -> str:
        count = self.store_repo.count_all() + 1
        return f"STORE-{count:03d}"

    def list_stores(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[StoreResponse]:
        stores = self.store_repo.list_all(skip=skip, limit=limit, is_active=is_active)
        return [StoreResponse.model_validate(s) for s in stores]

    def list_stores_with_stats(self, skip: int = 0, limit: int = 100) -> List[StoreWithStatsResponse]:
        stores = self.store_repo.list_all(skip=skip, limit=limit)
        results = []
        for s in stores:
            stats = self.store_repo.get_store_stats(s.id)
            resp = StoreWithStatsResponse(
                id=s.id,
                store_code=s.store_code,
                store_name=s.store_name,
                store_branch=s.store_branch,
                phone_number=s.phone_number,
                email=s.email,
                address=s.address,
                currency_symbol=s.currency_symbol,
                exchange_rate_khr=s.exchange_rate_khr,
                logo_url=s.logo_url,
                is_active=s.is_active,
                created_at=s.created_at,
                updated_at=s.updated_at,
                total_staff=stats["total_staff"],
                total_products=stats["total_products"],
                total_sales_count=stats["total_sales_count"],
                total_revenue=stats["total_revenue"],
            )
            results.append(resp)
        return results

    def get_by_id(self, store_id: int) -> StoreWithStatsResponse:
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        stats = self.store_repo.get_store_stats(store_id)
        return StoreWithStatsResponse(
            id=store.id,
            store_code=store.store_code,
            store_name=store.store_name,
            store_branch=store.store_branch,
            phone_number=store.phone_number,
            email=store.email,
            address=store.address,
            currency_symbol=store.currency_symbol,
            exchange_rate_khr=store.exchange_rate_khr,
            logo_url=store.logo_url,
            is_active=store.is_active,
            created_at=store.created_at,
            updated_at=store.updated_at,
            total_staff=stats["total_staff"],
            total_products=stats["total_products"],
            total_sales_count=stats["total_sales_count"],
            total_revenue=stats["total_revenue"],
        )

    def create_store(self, store_in: StoreCreate) -> StoreResponse:
        store_code = store_in.store_code
        if not store_code or not store_code.strip():
            store_code = self._generate_store_code()
            while self.store_repo.get_by_code(store_code):
                store_code = f"STORE-{random.randint(100, 999)}"
        else:
            store_code = store_code.strip().upper()
            if self.store_repo.get_by_code(store_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Store code '{store_code}' is already registered",
                )

        new_store = Store(
            store_code=store_code,
            store_name=store_in.store_name,
            store_branch=store_in.store_branch or "Main Branch",
            phone_number=store_in.phone_number,
            email=store_in.email,
            address=store_in.address,
            currency_symbol=store_in.currency_symbol or "$",
            exchange_rate_khr=store_in.exchange_rate_khr or 4100.0,
            logo_url=store_in.logo_url,
            is_active=True,
        )
        created_store = self.store_repo.create(new_store)

        # Initialize default settings for this store
        default_setting = StoreSetting(
            store_id=created_store.id,
            printer_name="Bluetooth 80mm POS Thermal",
            printer_paper_width=80,
            auto_print_receipt=True,
            sound_alert=True,
            receipt_header=f"Welcome to {created_store.store_name}",
            receipt_footer="Thank you for your visit! Please come again.",
        )
        self.db.add(default_setting)

        # Initialize default categories for this store
        default_categories = [
            {"name": "Coffee", "code": "coffee", "icon": "local_cafe"},
            {"name": "Tea & Milk", "code": "tea_milk", "icon": "emoji_food_beverage"},
            {"name": "Bakery", "code": "bakery", "icon": "bakery_dining"},
            {"name": "Beverages", "code": "beverages", "icon": "liquor"},
        ]
        for c in default_categories:
            cat = Category(
                store_id=created_store.id,
                name=c["name"],
                code=c["code"],
                icon=c["icon"],
            )
            self.db.add(cat)

        self.db.commit()
        return StoreResponse.model_validate(created_store)

    def update_store(self, store_id: int, store_in: StoreUpdate) -> StoreResponse:
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        for key, val in store_in.model_dump(exclude_unset=True).items():
            setattr(store, key, val)

        updated = self.store_repo.update(store)
        return StoreResponse.model_validate(updated)

    def deactivate_store(self, store_id: int) -> dict:
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        store.is_active = False
        self.store_repo.update(store)
        return {"message": f"Store '{store.store_name}' deactivated successfully"}
