from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_tenant_store_id
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse])
def list_customers(
    query: Optional[str] = Query(None, description="Search by name or phone"),
    skip: int = 0,
    limit: int = 100,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    return service.list_customers(store_id=store_id, skip=skip, limit=limit, query=query)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    return service.get_by_id(customer_id, store_id=store_id)


@router.post("", response_model=CustomerResponse)
def create_customer(
    customer_in: CustomerCreate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    return service.create_customer(customer_in, store_id=store_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    return service.update_customer(customer_id, customer_in, store_id=store_id)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    store_id: int = Depends(get_tenant_store_id),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    return service.delete_customer(customer_id, store_id=store_id)
