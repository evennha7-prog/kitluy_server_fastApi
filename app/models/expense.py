from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(100), default="Utilities")  # Utilities, Rent, Ingredients, Supplies, Salaries, Other
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    note = Column(Text, nullable=True)
    recorded_by = Column(String(100), default="Admin")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_expenses_store_date", "store_id", "date"),
        Index("ix_expenses_store_category", "store_id", "category"),
    )

    store = relationship("Store", back_populates="expenses")

