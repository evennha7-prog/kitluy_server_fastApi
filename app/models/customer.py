from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(50), index=True, nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    points = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("store_id", "phone", name="uq_store_customer_phone"),
        Index("ix_customers_store_active", "store_id", "is_active"),
    )

    store = relationship("Store", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")

