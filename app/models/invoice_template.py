from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserInvoiceTemplate(Base):
    __tablename__ = "user_invoice_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)

    # Style & Paper Format
    style = Column(String(50), default="minimal")  # 'minimal', 'cafeClassic', 'retailCompact', 'taxOfficial'
    paper_size = Column(String(20), default="80mm")  # '58mm', '80mm', 'A4'

    # Store Branding & Info
    store_name = Column(String(255), default="KITLUY Coffee & Bakery")
    branch_name = Column(String(255), default="Main Branch")
    phone_number = Column(String(100), default="097 534 8338 / 012 345 678")
    address = Column(String(255), default="#128 St 2004, Phnom Penh")
    vat_tin = Column(String(100), default="K001-902345890")

    # Custom Notes
    header_message = Column(Text, default="សូមស្វាគមន៍មកកាន់ហាងយើងខ្ញុំ! Welcome!")
    footer_message = Column(Text, default="ទំនិញទិញរួចមិនអាចប្តូរវិញបានទេ\nThank you & See you again!")
    wifi_info = Column(String(255), default="Wi-Fi: KITLUY_GUEST / Pass: 88888888")

    # Feature Toggles
    show_logo = Column(Boolean, default=True)
    show_khqr = Column(Boolean, default=True)
    show_barcode = Column(Boolean, default=True)
    show_cashier = Column(Boolean, default=True)
    show_table_num = Column(Boolean, default=True)
    show_exchange_rate = Column(Boolean, default=True)
    show_vat_details = Column(Boolean, default=True)
    show_wifi_info = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", foreign_keys=[user_id])
    store = relationship("Store", foreign_keys=[store_id])
