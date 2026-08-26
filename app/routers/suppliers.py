from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierResponse])
def list_suppliers(
    query: Optional[str] = Query(None, description="Search by name, company, or phone"),
    skip: int = 0,
    limit: int = 100,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SupplierService(db)
    return service.list_suppliers(store_id=store_id, skip=skip, limit=limit, query=query)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SupplierService(db)
    return service.get_by_id(supplier_id, store_id=store_id)


@router.post("", response_model=SupplierResponse)
def create_supplier(
    supplier_in: SupplierCreate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SupplierService(db)
    return service.create_supplier(supplier_in, store_id=store_id)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_in: SupplierUpdate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SupplierService(db)
    return service.update_supplier(supplier_id, supplier_in, store_id=store_id)


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = SupplierService(db)
    return service.delete_supplier(supplier_id, store_id=store_id)
