from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    company_name = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    category = Column(String(100), default="Coffee Beans & Dairy")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    store = relationship("Store", back_populates="suppliers")
    purchases = relationship("Purchase", back_populates="supplier")
