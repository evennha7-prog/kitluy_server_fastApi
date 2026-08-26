from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class StoreSetting(Base):
    __tablename__ = "store_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    
    # Receipt Printer Settings
    printer_name = Column(String(100), default="Bluetooth 80mm POS Thermal")
    printer_paper_width = Column(Integer, default=80)
    auto_print_receipt = Column(Boolean, default=True)
    sound_alert = Column(Boolean, default=True)
    receipt_header = Column(String(255), default="Welcome to AudiCafe Retail POS")
    receipt_footer = Column(String(255), default="Thank you! Please come again.")
    
    # Telegram Bot
    telegram_bot_token = Column(String(255), nullable=True)
    telegram_chat_id = Column(String(100), nullable=True)
    telegram_alerts_enabled = Column(Boolean, default=False)
    
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    store = relationship("Store", back_populates="settings")
