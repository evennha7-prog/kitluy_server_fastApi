from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    code = Column(String(50), index=True, nullable=False)  # coffee, tea_milk, bakery, beverages
    icon = Column(String(50), default="category")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("store_id", "code", name="uq_store_category_code"),
        Index("ix_categories_store_active", "store_id", "is_active"),
    )

    store = relationship("Store", back_populates="categories")
    products = relationship("Product", back_populates="category_rel")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    barcode = Column(String(100), index=True, nullable=False)
    category = Column(String(100), default="coffee", index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0.0)
    stock_qty = Column(Integer, default=100)
    color = Column(String(50), default="#2E7D32", nullable=True)
    image_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("store_id", "barcode", name="uq_store_product_barcode"),
        Index("ix_products_store_active", "store_id", "is_active"),
        Index("ix_products_store_category", "store_id", "category"),
    )

    store = relationship("Store", back_populates="products")
    category_rel = relationship("Category", back_populates="products")

