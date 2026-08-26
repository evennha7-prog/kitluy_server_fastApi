from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse


class SupplierService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SupplierRepository(db)

    def list_suppliers(self, store_id: int, skip: int = 0, limit: int = 100, query: Optional[str] = None) -> List[SupplierResponse]:
        suppliers = self.repo.list_suppliers(store_id=store_id, skip=skip, limit=limit, query=query)
        return [SupplierResponse.model_validate(s) for s in suppliers]

    def get_by_id(self, supplier_id: int, store_id: Optional[int] = None) -> SupplierResponse:
        supplier = self.repo.get_by_id(supplier_id, store_id=store_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return SupplierResponse.model_validate(supplier)

    def create_supplier(self, supplier_in: SupplierCreate, store_id: int) -> SupplierResponse:
        supplier = Supplier(
            store_id=store_id,
            name=supplier_in.name,
            company_name=supplier_in.company_name,
            phone=supplier_in.phone.strip(),
            email=supplier_in.email,
            address=supplier_in.address,
            category=supplier_in.category or "Coffee Beans & Dairy",
        )
        created = self.repo.create(supplier)
        return SupplierResponse.model_validate(created)

    def update_supplier(self, supplier_id: int, supplier_in: SupplierUpdate, store_id: int) -> SupplierResponse:
        supplier = self.repo.get_by_id(supplier_id, store_id=store_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        if supplier_in.name is not None:
            supplier.name = supplier_in.name
        if supplier_in.company_name is not None:
            supplier.company_name = supplier_in.company_name
        if supplier_in.phone is not None:
            supplier.phone = supplier_in.phone.strip()
        if supplier_in.email is not None:
            supplier.email = supplier_in.email
        if supplier_in.address is not None:
            supplier.address = supplier_in.address
        if supplier_in.category is not None:
            supplier.category = supplier_in.category
        if supplier_in.is_active is not None:
            supplier.is_active = supplier_in.is_active

        updated = self.repo.update(supplier)
        return SupplierResponse.model_validate(updated)

    def delete_supplier(self, supplier_id: int, store_id: int) -> dict:
        supplier = self.repo.get_by_id(supplier_id, store_id=store_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        self.repo.delete(supplier)
        return {"message": "Supplier removed"}
