from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    invoice_no = Column(String(50), index=True, nullable=False)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cashier_name = Column(String(100), default="Cashier")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(100), default="General Customer")
    customer_phone = Column(String(50), nullable=True)
    
    subtotal = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    
    payment_method = Column(String(50), default="CASH")  # CASH, ABA_KHQR, CARD
    payment_status = Column(String(50), default="PAID")  # PAID, PENDING, CANCELLED
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        UniqueConstraint("store_id", "invoice_no", name="uq_store_invoice_no"),
        Index("ix_sales_store_created", "store_id", "created_at"),
        Index("ix_sales_store_status_created", "store_id", "payment_status", "created_at"),
    )

    store = relationship("Store", back_populates="sales")
    cashier = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan", lazy="selectin")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    product_name = Column(String(150), nullable=False)
    barcode = Column(String(100), nullable=True)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)

    __table_args__ = (
        Index("ix_sale_items_store_prod", "store_id", "product_id"),
    )

    sale = relationship("Sale", back_populates="items")

