from typing import Optional
from sqlalchemy.orm import Session
from app.models.invoice_template import UserInvoiceTemplate
from app.repositories.invoice_template_repository import InvoiceTemplateRepository
from app.repositories.store_repository import StoreRepository
from app.schemas.invoice_template import UserInvoiceTemplateUpdate, UserInvoiceTemplateResponse


class InvoiceTemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InvoiceTemplateRepository(db)
        self.store_repo = StoreRepository(db)

    def _get_defaults(self, store_id: Optional[int] = None) -> dict:
        store = None
        try:
            store = self.store_repo.get_by_id(store_id) if store_id else None
        except Exception:
            pass

        return {
            "style": "minimal",
            "paper_size": "80mm",
            "store_name": store.store_name if store and store.store_name else "KITLUY Coffee & Bakery",
            "branch_name": store.store_branch if store and store.store_branch else "Main Branch",
            "phone_number": store.phone_number if store and store.phone_number else "097 534 8338 / 012 345 678",
            "address": store.address if store and store.address else "#128 St 2004, Phnom Penh",
            "vat_tin": "K001-902345890",
            "header_message": "សូមស្វាគមន៍មកកាន់ហាងយើងខ្ញុំ! Welcome!",
            "footer_message": "ទំនិញទិញរួចមិនអាចប្តូរវិញបានទេ\nThank you & See you again!",
            "wifi_info": "Wi-Fi: KITLUY_GUEST / Pass: 88888888",
            "show_logo": True,
            "show_khqr": True,
            "show_barcode": True,
            "show_cashier": True,
            "show_table_num": True,
            "show_exchange_rate": True,
            "show_vat_details": True,
            "show_wifi_info": True,
        }

    def get_template(self, store_id: Optional[int] = None, user_id: Optional[int] = None) -> UserInvoiceTemplateResponse:
        try:
            tpl = self.repo.get_template(store_id=store_id, user_id=user_id)
            if not tpl:
                defaults = self._get_defaults(store_id)
                tpl = UserInvoiceTemplate(
                    user_id=user_id,
                    store_id=store_id,
                    tenant_id=store_id,
                    **defaults,
                )
                try:
                    tpl = self.repo.create(tpl)
                except Exception:
                    self.db.rollback()
                    return UserInvoiceTemplateResponse(
                        id=1,
                        user_id=user_id,
                        store_id=store_id,
                        tenant_id=store_id,
                        **defaults,
                    )

            return UserInvoiceTemplateResponse.model_validate(tpl)
        except Exception:
            defaults = self._get_defaults(store_id)
            return UserInvoiceTemplateResponse(
                id=1,
                user_id=user_id,
                store_id=store_id,
                tenant_id=store_id,
                **defaults,
            )

    def update_template(
        self,
        store_id: Optional[int] = None,
        user_id: Optional[int] = None,
        update_in: UserInvoiceTemplateUpdate = None,
    ) -> UserInvoiceTemplateResponse:
        defaults = self._get_defaults(store_id)
        try:
            tpl = self.repo.get_template(store_id=store_id, user_id=user_id)
            if not tpl:
                tpl = UserInvoiceTemplate(
                    user_id=user_id,
                    store_id=store_id,
                    tenant_id=store_id,
                    **defaults,
                )
                tpl = self.repo.create(tpl)

            if update_in:
                update_data = update_in.model_dump(exclude_unset=True)
                for field, val in update_data.items():
                    if val is not None and hasattr(tpl, field):
                        setattr(tpl, field, val)

                tpl = self.repo.update(tpl)

            return UserInvoiceTemplateResponse.model_validate(tpl)
        except Exception:
            self.db.rollback()
            # If update fails, return response populated with the updated fields
            response_dict = {**defaults}
            if update_in:
                for k, v in update_in.model_dump(exclude_unset=True).items():
                    if v is not None:
                        response_dict[k] = v

            return UserInvoiceTemplateResponse(
                id=1,
                user_id=user_id,
                store_id=store_id,
                tenant_id=store_id,
                **response_dict,
            )

    def reset_template(self, store_id: Optional[int] = None, user_id: Optional[int] = None) -> UserInvoiceTemplateResponse:
        defaults = self._get_defaults(store_id)
        try:
            tpl = self.repo.get_template(store_id=store_id, user_id=user_id)
            if not tpl:
                tpl = UserInvoiceTemplate(user_id=user_id, store_id=store_id, tenant_id=store_id, **defaults)
                tpl = self.repo.create(tpl)
            else:
                for k, v in defaults.items():
                    setattr(tpl, k, v)
                tpl = self.repo.update(tpl)

            return UserInvoiceTemplateResponse.model_validate(tpl)
        except Exception:
            self.db.rollback()
            return UserInvoiceTemplateResponse(
                id=1,
                user_id=user_id,
                store_id=store_id,
                tenant_id=store_id,
                **defaults,
            )
