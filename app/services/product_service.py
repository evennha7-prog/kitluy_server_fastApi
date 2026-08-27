import random
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product, Category
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, CategoryCreate, CategoryUpdate, CategoryResponse


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)

    def _generate_barcode(self) -> str:
        # Generate 12-digit UPC / EAN barcode e.g. 884500000000
        return f"884{random.randint(100000000, 999999999)}"

    def list_products(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[ProductResponse]:
        products = self.product_repo.list_products(
            store_id=store_id, skip=skip, limit=limit, category=category, query=query
        )
        return [ProductResponse.model_validate(p) for p in products]

    def get_by_id(self, product_id: int, store_id: int) -> ProductResponse:
        product = self.product_repo.get_by_id(product_id, store_id=store_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductResponse.model_validate(product)

    def get_by_barcode(self, barcode: str, store_id: int) -> ProductResponse:
        product = self.product_repo.get_by_barcode(barcode.strip(), store_id=store_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product with given barcode not found")
        return ProductResponse.model_validate(product)

    def create_product(self, product_in: ProductCreate, store_id: int) -> ProductResponse:
        barcode = product_in.barcode.strip() if product_in.barcode else self._generate_barcode()

        existing = self.product_repo.get_by_barcode(barcode, store_id=store_id)
        if existing:
            raise HTTPException(status_code=400, detail="Barcode already assigned to another item in this store")

        valid_cat_id = None
        if product_in.category_id and product_in.category_id > 0:
            cat = self.db.query(Category).filter(Category.id == product_in.category_id, Category.store_id == store_id).first()
            if cat:
                valid_cat_id = cat.id

        product = Product(
            store_id=store_id,
            tenant_id=store_id,
            name=product_in.name,
            barcode=barcode,
            category=product_in.category or "coffee",
            price=product_in.price,
            cost_price=product_in.cost_price or 0.0,
            stock_qty=product_in.stock_qty if product_in.stock_qty is not None else 100,
            color=product_in.color or "#2E7D32",
            image_url=product_in.image_url,
            description=product_in.description,
            category_id=valid_cat_id,
            is_active=True,
        )
        created = self.product_repo.create(product)
        return ProductResponse.model_validate(created)

    def update_product(self, product_id: int, product_in: ProductUpdate, store_id: int) -> ProductResponse:
        product = self.product_repo.get_by_id(product_id, store_id=store_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product_in.name is not None:
            product.name = product_in.name
        if product_in.barcode is not None:
            existing = self.product_repo.get_by_barcode(product_in.barcode.strip(), store_id=store_id)
            if existing and existing.id != product_id:
                raise HTTPException(status_code=400, detail="Barcode already assigned to another item in this store")
            product.barcode = product_in.barcode.strip()
        if product_in.category is not None:
            product.category = product_in.category
        if product_in.price is not None:
            product.price = product_in.price
        if product_in.cost_price is not None:
            product.cost_price = product_in.cost_price
        if product_in.stock_qty is not None:
            product.stock_qty = product_in.stock_qty
        if product_in.color is not None:
            product.color = product_in.color
        if product_in.image_url is not None:
            product.image_url = product_in.image_url
        if product_in.description is not None:
            product.description = product_in.description
        if product_in.is_active is not None:
            product.is_active = product_in.is_active
        if product_in.category_id is not None:
            valid_cat_id = None
            if product_in.category_id > 0:
                cat = self.db.query(Category).filter(Category.id == product_in.category_id, Category.store_id == store_id).first()
                if cat:
                    valid_cat_id = cat.id
            product.category_id = valid_cat_id

        updated = self.product_repo.update(product)
        return ProductResponse.model_validate(updated)

    def delete_product(self, product_id: int, store_id: int) -> dict:
        product = self.product_repo.get_by_id(product_id, store_id=store_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        self.product_repo.delete(product)
        return {"message": "Product deleted successfully"}

    def list_categories(self, store_id: int) -> List[CategoryResponse]:
        categories = self.product_repo.list_categories(store_id=store_id)
        return [CategoryResponse.model_validate(c) for c in categories]

    def get_category(self, category_id: int, store_id: int) -> CategoryResponse:
        category = self.product_repo.get_category_by_id(category_id, store_id=store_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return CategoryResponse.model_validate(category)

    def create_category(self, category_in: CategoryCreate, store_id: int) -> CategoryResponse:
        code = category_in.code.strip().lower().replace(" ", "_")
        existing = self.product_repo.get_category_by_code(code, store_id=store_id)
        if existing:
            raise HTTPException(status_code=400, detail="Category with this code already exists")

        category = Category(
            store_id=store_id,
            name=category_in.name.strip(),
            code=code,
            icon=category_in.icon or "category",
            is_active=True,
        )
        created = self.product_repo.create_category(category)
        return CategoryResponse.model_validate(created)

    def update_category(self, category_id: int, category_in: CategoryUpdate, store_id: int) -> CategoryResponse:
        category = self.product_repo.get_category_by_id(category_id, store_id=store_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category_in.name is not None:
            category.name = category_in.name.strip()
        if category_in.code is not None:
            code = category_in.code.strip().lower().replace(" ", "_")
            existing = self.product_repo.get_category_by_code(code, store_id=store_id)
            if existing and existing.id != category_id:
                raise HTTPException(status_code=400, detail="Category with this code already exists")
            category.code = code
        if category_in.icon is not None:
            category.icon = category_in.icon
        if category_in.is_active is not None:
            category.is_active = category_in.is_active

        updated = self.product_repo.update_category(category)
        return CategoryResponse.model_validate(updated)

    def delete_category(self, category_id: int, store_id: int) -> dict:
        category = self.product_repo.get_category_by_id(category_id, store_id=store_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        self.product_repo.delete_category(category)
        return {"message": "Category deleted successfully"}
