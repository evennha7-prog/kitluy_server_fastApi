from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True, index=True)
    supplier_name = Column(String(150), nullable=False)
    invoice_no = Column(String(50), index=True, nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), default="RECEIVED")  # RECEIVED, PENDING, CANCELLED
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        UniqueConstraint("store_id", "invoice_no", name="uq_store_purchase_invoice"),
        Index("ix_purchases_store_created", "store_id", "created_at"),
    )

    store = relationship("Store", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan", lazy="selectin")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    product_name = Column(String(150), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    __table_args__ = (
        Index("ix_purchase_items_store_prod", "store_id", "product_id"),
    )

    purchase = relationship("Purchase", back_populates="items")

