from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: int, store_id: Optional[int] = None) -> Optional[Customer]:
        query = self.db.query(Customer).filter(Customer.id == customer_id)
        if store_id is not None:
            query = query.filter(Customer.store_id == store_id)
        return query.first()

    def get_by_phone(self, phone: str, store_id: Optional[int] = None) -> Optional[Customer]:
        clean = phone.replace(" ", "").replace("-", "")
        query = self.db.query(Customer).filter(
            or_(Customer.phone == phone, Customer.phone == clean)
        )
        if store_id is not None:
            query = query.filter(Customer.store_id == store_id)
        return query.first()

    def list_customers(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        query: Optional[str] = None,
    ) -> List[Customer]:
        db_query = self.db.query(Customer).filter(Customer.store_id == store_id, Customer.is_active == True)
        if query:
            db_query = db_query.filter(
                or_(
                    Customer.name.ilike(f"%{query}%"),
                    Customer.phone.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                )
            )
        return db_query.offset(skip).limit(limit).all()

    def count_customers(self, store_id: int) -> int:
        return self.db.query(Customer).filter(Customer.store_id == store_id, Customer.is_active == True).count()

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer) -> Customer:
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.commit()
