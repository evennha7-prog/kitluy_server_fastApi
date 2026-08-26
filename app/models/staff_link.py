from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class StaffLink(Base):
    __tablename__ = "staffs_link"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_owner_id = Column(Integer, ForeignKey("store_owners.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    staff_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_title = Column(String(50), default="Cashier")  # Cashier, Barista, Inventory, Shift Supervisor
    permissions = Column(Text, default='["pos_sales", "discount"]')  # JSON list of permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    store_owner = relationship("StoreOwner", back_populates="staff_links")
    store = relationship("Store", foreign_keys=[store_id])
    staff_user = relationship("User", foreign_keys=[staff_user_id], backref="staff_link")
