from typing import Optional
from sqlalchemy.orm import Session
from app.models.invoice_template import UserInvoiceTemplate


class InvoiceTemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_template(self, store_id: Optional[int] = None, user_id: Optional[int] = None) -> Optional[UserInvoiceTemplate]:
        query = self.db.query(UserInvoiceTemplate)
        if store_id:
            tpl = query.filter(UserInvoiceTemplate.store_id == store_id).first()
            if tpl:
                return tpl
        if user_id:
            tpl = query.filter(UserInvoiceTemplate.user_id == user_id).first()
            if tpl:
                return tpl
        # Fallback to the first available template or None
        return query.first()

    def create(self, template: UserInvoiceTemplate) -> UserInvoiceTemplate:
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: UserInvoiceTemplate) -> UserInvoiceTemplate:
        self.db.commit()
        self.db.refresh(template)
        return template
