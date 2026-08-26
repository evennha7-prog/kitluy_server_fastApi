from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.product import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def list_categories(
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.list_categories(store_id=store_id)


@router.post("", response_model=CategoryResponse)
def create_category(
    category_in: CategoryCreate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.create_category(category_in, store_id=store_id)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_category(category_id, store_id=store_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.update_category(category_id, category_in, store_id=store_id)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.delete_category(category_id, store_id=store_id)
