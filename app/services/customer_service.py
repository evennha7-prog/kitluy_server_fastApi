from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse


class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CustomerRepository(db)

    def _to_response(self, c: Customer) -> CustomerResponse:
        return CustomerResponse(
            id=c.id,
            store_id=c.store_id,
            name=c.name,
            phone=c.phone,
            phone_number=c.phone,
            email=c.email,
            address=c.address,
            points=c.points or 0,
            total_orders=c.total_orders or 0,
            visits_count=c.total_orders or 0,
            total_spent=c.total_spent or 0.0,
            is_active=c.is_active,
            created_at=c.created_at,
        )

    def list_customers(self, store_id: int, skip: int = 0, limit: int = 100, query: Optional[str] = None) -> List[CustomerResponse]:
        customers = self.repo.list_customers(store_id=store_id, skip=skip, limit=limit, query=query)
        return [self._to_response(c) for c in customers]

    def get_by_id(self, customer_id: int, store_id: Optional[int] = None) -> CustomerResponse:
        customer = self.repo.get_by_id(customer_id, store_id=store_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return self._to_response(customer)

    def create_customer(self, customer_in: CustomerCreate, store_id: int) -> CustomerResponse:
        raw_phone = customer_in.phone or customer_in.phone_number or ""
        phone = raw_phone.strip()
        if not phone:
            raise HTTPException(status_code=400, detail="Customer phone number is required")

        existing = self.repo.get_by_phone(phone, store_id=store_id)
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone already exists in your store")

        customer = Customer(
            store_id=store_id,
            tenant_id=store_id,
            name=customer_in.name.strip(),
            phone=phone,
            email=customer_in.email,
            address=customer_in.address,
            points=0,
            total_orders=0,
            total_spent=0.0,
            is_active=True,
        )
        created = self.repo.create(customer)
        return self._to_response(created)

    def update_customer(self, customer_id: int, customer_in: CustomerUpdate, store_id: int) -> CustomerResponse:
        customer = self.repo.get_by_id(customer_id, store_id=store_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        if customer_in.name is not None:
            customer.name = customer_in.name.strip()
        raw_phone = customer_in.phone or customer_in.phone_number
        if raw_phone is not None:
            customer.phone = raw_phone.strip()
        if customer_in.email is not None:
            customer.email = customer_in.email
        if customer_in.address is not None:
            customer.address = customer_in.address
        if customer_in.is_active is not None:
            customer.is_active = customer_in.is_active

        updated = self.repo.update(customer)
        return self._to_response(updated)

    def delete_customer(self, customer_id: int, store_id: int) -> dict:
        customer = self.repo.get_by_id(customer_id, store_id=store_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        self.repo.delete(customer)
        return {"message": "Customer removed"}
