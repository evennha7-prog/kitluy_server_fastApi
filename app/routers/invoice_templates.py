from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id, get_optional_current_user
from app.schemas.invoice_template import UserInvoiceTemplateUpdate, UserInvoiceTemplateResponse
from app.services.invoice_template_service import InvoiceTemplateService

router = APIRouter(prefix="/invoice-template", tags=["User Invoice Template"])


@router.get("", response_model=UserInvoiceTemplateResponse)
def get_invoice_template(
    store_id: int = Depends(get_tenant_store_id),
    current_user = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    service = InvoiceTemplateService(db)
    user_id = current_user.id if current_user else None
    return service.get_template(store_id=store_id, user_id=user_id)


@router.put("", response_model=UserInvoiceTemplateResponse)
def update_invoice_template(
    update_in: UserInvoiceTemplateUpdate,
    store_id: int = Depends(get_tenant_store_id),
    current_user = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    service = InvoiceTemplateService(db)
    user_id = current_user.id if current_user else None
    return service.update_template(store_id=store_id, user_id=user_id, update_in=update_in)


@router.post("/reset", response_model=UserInvoiceTemplateResponse)
def reset_invoice_template(
    store_id: int = Depends(get_tenant_store_id),
    current_user = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    service = InvoiceTemplateService(db)
    user_id = current_user.id if current_user else None
    return service.reset_template(store_id=store_id, user_id=user_id)
