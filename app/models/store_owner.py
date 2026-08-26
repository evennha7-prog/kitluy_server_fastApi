from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class StoreOwner(Base):
    __tablename__ = "store_owners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    status = Column(String(30), default="pending", index=True)  # pending, approved, rejected, active, suspended
    business_type = Column(String(100), default="Cafe & Beverage")
    business_license = Column(String(255), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="owner_profile")
    store = relationship("Store", foreign_keys=[store_id], backref="store_owner")
    approver = relationship("User", foreign_keys=[approved_by])
    staff_links = relationship("StaffLink", back_populates="store_owner", cascade="all, delete-orphan")
