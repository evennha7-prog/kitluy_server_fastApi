from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product, Category


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int, store_id: Optional[int] = None) -> Optional[Product]:
        query = self.db.query(Product).filter(Product.id == product_id)
        if store_id is not None:
            query = query.filter(Product.store_id == store_id)
        return query.first()

    def get_by_ids(self, product_ids: List[int], store_id: Optional[int] = None) -> List[Product]:
        if not product_ids:
            return []
        query = self.db.query(Product).filter(Product.id.in_(product_ids))
        if store_id is not None:
            query = query.filter(Product.store_id == store_id)
        return query.all()

    def get_by_barcode(self, barcode: str, store_id: Optional[int] = None) -> Optional[Product]:
        query = self.db.query(Product).filter(Product.barcode == barcode)
        if store_id is not None:
            query = query.filter(Product.store_id == store_id)
        return query.first()

    def get_by_barcodes(self, barcodes: List[str], store_id: Optional[int] = None) -> List[Product]:
        if not barcodes:
            return []
        query = self.db.query(Product).filter(Product.barcode.in_(barcodes))
        if store_id is not None:
            query = query.filter(Product.store_id == store_id)
        return query.all()


    def list_products(
        self,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        query: Optional[str] = None,
        is_active: bool = True,
    ) -> List[Product]:
        db_query = self.db.query(Product).filter(Product.store_id == store_id, Product.is_active == is_active)

        if category:
            db_query = db_query.filter(Product.category == category)
        if query:
            db_query = db_query.filter(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.barcode.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                )
            )
        return db_query.offset(skip).limit(limit).all()

    def count_products(self, store_id: int, is_active: bool = True) -> int:
        return self.db.query(Product).filter(Product.store_id == store_id, Product.is_active == is_active).count()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

    # Category operations
    def list_categories(self, store_id: int) -> List[Category]:
        return self.db.query(Category).filter(Category.store_id == store_id, Category.is_active == True).all()

    def get_category_by_id(self, category_id: int, store_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id, Category.store_id == store_id).first()

    def get_category_by_code(self, code: str, store_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.code == code, Category.store_id == store_id).first()

    def create_category(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()
