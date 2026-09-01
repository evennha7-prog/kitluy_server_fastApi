from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.setting import StoreSetting
from app.repositories.setting_repository import SettingRepository
from app.repositories.store_repository import StoreRepository
from app.schemas.setting import StoreSettingUpdate, StoreSettingResponse


class SettingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SettingRepository(db)
        self.store_repo = StoreRepository(db)

    def get_settings(self, store_id: int) -> StoreSettingResponse:
        store = self.store_repo.get_by_id(store_id)
        if not store:
            stores = self.store_repo.list_all(limit=1)
            if stores:
                store = stores[0]
                store_id = store.id

        settings = self.repo.get_settings(store_id=store_id)
        if not settings and store_id:
            try:
                # Create default setting if missing
                settings = StoreSetting(
                    store_id=store_id,
                    printer_name="Bluetooth 80mm POS Thermal",
                    printer_paper_width=80,
                    auto_print_receipt=True,
                    sound_alert=True,
                    receipt_header=f"Welcome to {store.store_name if store else 'POS'}",
                    receipt_footer="Thank you for your visit! Please come again.",
                )
                settings = self.repo.create(settings)
            except Exception:
                self.db.rollback()
                settings = self.repo.get_settings(store_id=store_id)

        return StoreSettingResponse(
            id=settings.id if settings else 1,
            store_id=store_id,
            store_name=store.store_name if store else "POS Store",
            store_branch=store.store_branch if store else "Main Branch",
            phone_number=store.phone_number or "" if store else "",
            email=store.email or "" if store else "",
            address=store.address or "" if store else "",
            currency_symbol=store.currency_symbol if store else "$",
            exchange_rate_khr=store.exchange_rate_khr if store else 4100.0,
            tax_rate=0.0,
            printer_name=settings.printer_name if settings else "Bluetooth 80mm POS Thermal",
            printer_paper_width=settings.printer_paper_width if settings else 80,
            auto_print_receipt=settings.auto_print_receipt if settings else True,
            sound_alert=settings.sound_alert if settings else True,
            receipt_header=settings.receipt_header if settings else "Welcome to POS",
            receipt_footer=settings.receipt_footer if settings else "Thank you for your visit! Please come again.",
            telegram_alerts_enabled=settings.telegram_alerts_enabled if settings else False,
        )

    def update_settings(self, store_id: int, update_in: StoreSettingUpdate) -> StoreSettingResponse:
        store = self.store_repo.get_by_id(store_id)
        if not store:
            stores = self.store_repo.list_all(limit=1)
            if stores:
                store = stores[0]
                store_id = store.id

        settings = self.repo.get_settings(store_id=store_id)
        if not settings and store_id:
            try:
                settings = StoreSetting(store_id=store_id)
                settings = self.repo.create(settings)
            except Exception:
                self.db.rollback()
                settings = self.repo.get_settings(store_id=store_id)

        # Update store properties if provided
        if store:
            if update_in.store_name is not None:
                store.store_name = update_in.store_name
            if update_in.store_branch is not None:
                store.store_branch = update_in.store_branch
            if update_in.phone_number is not None:
                store.phone_number = update_in.phone_number
            if update_in.email is not None:
                store.email = update_in.email
            if update_in.address is not None:
                store.address = update_in.address
            if update_in.currency_symbol is not None:
                store.currency_symbol = update_in.currency_symbol
            if update_in.exchange_rate_khr is not None:
                store.exchange_rate_khr = update_in.exchange_rate_khr
            self.store_repo.update(store)

        # Update printer / telegram settings
        if settings:
            for key in ["printer_name", "printer_paper_width", "auto_print_receipt", "sound_alert", "receipt_header", "receipt_footer", "telegram_bot_token", "telegram_chat_id", "telegram_alerts_enabled"]:
                val = getattr(update_in, key, None)
                if val is not None:
                    setattr(settings, key, val)
            self.repo.update(settings)

        return self.get_settings(store_id=store_id)

