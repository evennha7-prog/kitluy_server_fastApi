from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_super_admin
from app.models.user import User
from app.models.store import Store
from app.repositories.user_repository import UserRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.sale_repository import SaleRepository
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreWithStatsResponse
from app.schemas.user import UserResponse
from app.services.store_service import StoreService

router = APIRouter(prefix="/admin", tags=["Super Administrator (Platform Owner)"])


@router.get("/dashboard")
def get_super_admin_dashboard(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    store_repo = StoreRepository(db)
    user_repo = UserRepository(db)
    stores = store_repo.list_all(limit=1000)
    
    total_stores = len(stores)
    active_stores = sum(1 for s in stores if s.is_active)
    total_users = len(user_repo.list_all(limit=5000))
    
    # Calculate total platform volume
    total_platform_revenue = 0.0
    for s in stores:
        stats = store_repo.get_store_stats(s.id)
        total_platform_revenue += stats["total_revenue"]

    return {
        "platform_name": "KITLUY SaaS POS Engine",
        "super_admin": current_user.full_name,
        "total_stores": total_stores,
        "active_stores": active_stores,
        "total_users": total_users,
        "total_platform_revenue": round(total_platform_revenue, 2),
    }


@router.get("/stores", response_model=List[StoreWithStatsResponse])
def list_stores(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.list_stores_with_stats(skip=skip, limit=limit)


@router.get("/stores/{store_id}", response_model=StoreWithStatsResponse)
def get_store(
    store_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.get_by_id(store_id)


@router.post("/stores", response_model=StoreResponse)
def create_store(
    store_in: StoreCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.create_store(store_in)


@router.put("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store_in: StoreUpdate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.update_store(store_id, store_in)


@router.delete("/stores/{store_id}")
def deactivate_store(
    store_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.deactivate_store(store_id)


@router.get("/stores/{store_id}/staff", response_model=List[UserResponse])
def get_store_staff(
    store_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    staff_members = user_repo.list_by_store(store_id)
    return [UserResponse.model_validate(u) for u in staff_members]
