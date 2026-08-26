from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, CategoryCreate, CategoryResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products & Catalog"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category code"),
    query: Optional[str] = Query(None, description="Search query by name, barcode, or desc"),
    skip: int = 0,
    limit: int = 100,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.list_products(store_id=store_id, skip=skip, limit=limit, category=category, query=query)


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.list_categories(store_id=store_id)


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category_in: CategoryCreate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.create_category(category_in, store_id=store_id)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.delete_category(category_id, store_id=store_id)


@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_product_by_barcode(
    barcode: str,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_by_barcode(barcode, store_id=store_id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_by_id(product_id, store_id=store_id)


@router.post("", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.create_product(product_in, store_id=store_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.update_product(product_id, product_in, store_id=store_id)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.delete_product(product_id, store_id=store_id)
