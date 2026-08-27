from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    pin_code = Column(String(10), nullable=True)  # 4-digit POS Cashier PIN
    role = Column(String(50), default="cashier")  # super_admin, store_admin, cashier, stock_admin
    shift = Column(String(100), default="Morning Shift (06:30 AM - 03:00 PM)")
    telegram_username = Column(String(100), nullable=True)
    avatar_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    store = relationship("Store", back_populates="users")
    sales = relationship("Sale", back_populates="cashier")
