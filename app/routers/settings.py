from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.setting import StoreSettingUpdate, StoreSettingResponse
from app.services.setting_service import SettingService

router = APIRouter(prefix="/settings", tags=["Store Settings & Hardware"])


@router.get("", response_model=StoreSettingResponse)
def get_settings(
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SettingService(db)
    return service.get_settings(store_id=store_id)


@router.put("", response_model=StoreSettingResponse)
def update_settings(
    update_in: StoreSettingUpdate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SettingService(db)
    return service.update_settings(store_id=store_id, update_in=update_in)
