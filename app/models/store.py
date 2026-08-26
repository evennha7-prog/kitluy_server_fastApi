from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., STORE-001, AUDI-PP
    tenant_id = Column(String(50), index=True, nullable=True)  # Global Multi-tenant key
    store_name = Column(String(150), nullable=False, index=True)
    store_branch = Column(String(100), default="Main Branch")
    phone_number = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    currency_symbol = Column(String(10), default="$")
    exchange_rate_khr = Column(Float, default=4100.0)
    logo_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    users = relationship("User", back_populates="store", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="store", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="store", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="store", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="store", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="store", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="store", cascade="all, delete-orphan")
    settings = relationship("StoreSetting", back_populates="store", uselist=False, cascade="all, delete-orphan")
