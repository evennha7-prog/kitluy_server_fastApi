from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.store import Store
from app.models.user import User
from app.models.store_owner import StoreOwner
from app.models.staff_link import StaffLink
from app.models.product import Product, Category
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.expense import Expense
from app.models.sale import Sale, SaleItem
from app.models.setting import StoreSetting


def seed_initial_data(db: Session):
    # 1. Seed Platform Super Administrator
    if not db.query(User).filter(User.phone_number == "071 00 00 000").first():
        super_admin = User(
            full_name="Platform Super Administrator",
            phone_number="071 00 00 000",
            email="superadmin@kitluypos.com",
            hashed_password=get_password_hash("admin123"),
            pin_code="9999",
            role="super_admin",
            shift="Platform Management",
            telegram_username="@kitluy_superadmin",
            avatar_index=0,
            is_active=True,
            store_id=None,
        )
        db.add(super_admin)
        db.flush()

    # 2. Seed Store 1 (AudiCafe - Main Branch)
    store1 = db.query(Store).filter(Store.store_code == "STORE-001").first()
    if not store1:
        store1 = Store(
            store_code="STORE-001",
            store_name="AudiCafe",
            store_branch="Main Branch - Phnom Penh",
            phone_number="071 93 93 991",
            email="manager@audicafe.com",
            address="St. 2004, Phnom Penh, Cambodia",
            currency_symbol="$",
            exchange_rate_khr=4100.0,
            is_active=True,
        )
        db.add(store1)
        db.flush()

        # Store 1 Settings
        setting1 = StoreSetting(
            store_id=store1.id,
            printer_name="Bluetooth 80mm POS Thermal",
            printer_paper_width=80,
            auto_print_receipt=True,
            sound_alert=True,
            receipt_header="Welcome to AudiCafe (Main Branch)",
            receipt_footer="Thank you for your visit! Please come again.",
        )
        db.add(setting1)

    # 3. Seed Store 1 Users (Store Admin & Cashier)
    admin1 = db.query(User).filter(User.phone_number == "071 93 93 991").first()
    if not admin1:
        admin1 = User(
            store_id=store1.id,
            full_name="Prak Panha",
            phone_number="071 93 93 991",
            email="manager@audicafe.com",
            hashed_password=get_password_hash("123456"),
            pin_code="1234",
            role="store_admin",
            shift="Full-Time (06:30 AM - 05:00 PM)",
            telegram_username="@audicafe_pos",
            avatar_index=0,
            is_active=True,
        )
        db.add(admin1)
        db.flush()

    # Seed Store 1 StoreOwner record
    owner1 = db.query(StoreOwner).filter(StoreOwner.user_id == admin1.id).first()
    if not owner1:
        owner1 = StoreOwner(
            user_id=admin1.id,
            store_id=store1.id,
            status="approved",
            business_type="Cafe & Beverage",
            business_license="BL-2026-PP01",
            approved_at=datetime.now(timezone.utc),
        )
        db.add(owner1)
        db.flush()

    cashier1 = db.query(User).filter(User.phone_number == "012 888 999").first()
    if not cashier1:
        cashier1 = User(
            store_id=store1.id,
            full_name="Sophea Sok",
            phone_number="012 888 999",
            email="sophea@audicafe.com",
            hashed_password=get_password_hash("123456"),
            pin_code="0000",
            role="cashier",
            shift="Morning Shift (06:30 AM - 03:00 PM)",
            telegram_username="@sophea_pos",
            avatar_index=1,
            is_active=True,
        )
        db.add(cashier1)
        db.flush()

    # Seed Store 1 StaffLink record in staffs_link
    if not db.query(StaffLink).filter(StaffLink.staff_user_id == cashier1.id).first():
        link1 = StaffLink(
            store_owner_id=owner1.id,
            store_id=store1.id,
            staff_user_id=cashier1.id,
            role_title="Cashier",
            permissions='["pos_sales", "discount"]',
            is_active=True,
        )
        db.add(link1)

    # 4. Seed Store 1 Categories & Products
    categories_data = [
        {"name": "Coffee", "code": "coffee", "icon": "local_cafe"},
        {"name": "Tea & Milk", "code": "tea_milk", "icon": "emoji_food_beverage"},
        {"name": "Bakery", "code": "bakery", "icon": "bakery_dining"},
        {"name": "Beverages", "code": "beverages", "icon": "liquor"},
    ]

    cat_map = {}
    for cat_item in categories_data:
        existing = db.query(Category).filter(
            Category.store_id == store1.id,
            Category.code == cat_item["code"],
        ).first()
        if not existing:
            new_cat = Category(
                store_id=store1.id,
                name=cat_item["name"],
                code=cat_item["code"],
                icon=cat_item["icon"],
            )
            db.add(new_cat)
            db.flush()
            cat_map[cat_item["code"]] = new_cat.id
        else:
            cat_map[cat_item["code"]] = existing.id

    products_data = [
        {
            "name": "Caramel Macchiato",
            "barcode": "884500129384",
            "category": "coffee",
            "price": 2.75,
            "cost_price": 1.10,
            "stock_qty": 150,
            "image_url": "https://images.unsplash.com/photo-1572442388796-11668ba69e53",
            "description": "Espresso with vanilla syrup, steamed milk, and caramel drizzle.",
        },
        {
            "name": "Iced Americano",
            "barcode": "884500129385",
            "category": "coffee",
            "price": 2.00,
            "cost_price": 0.60,
            "stock_qty": 200,
            "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5",
            "description": "Rich espresso shots topped with cold water and ice.",
        },
        {
            "name": "Iced Caffe Latte",
            "barcode": "884500129386",
            "category": "coffee",
            "price": 2.50,
            "cost_price": 0.90,
            "stock_qty": 180,
            "image_url": "https://images.unsplash.com/photo-1559496417-e7f25cb247f3",
            "description": "Smooth blend of espresso and cold fresh milk over ice.",
        },
        {
            "name": "Hot Cappuccino",
            "barcode": "884500129387",
            "category": "coffee",
            "price": 2.50,
            "cost_price": 0.85,
            "stock_qty": 120,
            "image_url": "https://images.unsplash.com/photo-1534778101976-62847782c213",
            "description": "Dark, rich espresso with a thick layer of creamy milk foam.",
        },
        {
            "name": "Matcha Green Tea Latte",
            "barcode": "884500129388",
            "category": "tea_milk",
            "price": 3.00,
            "cost_price": 1.20,
            "stock_qty": 100,
            "image_url": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a",
            "description": "Premium Japanese Uji matcha blended with fresh milk.",
        },
        {
            "name": "Brown Sugar Pearl Milk Tea",
            "barcode": "884500129389",
            "category": "tea_milk",
            "price": 2.80,
            "cost_price": 1.00,
            "stock_qty": 140,
            "image_url": "https://images.unsplash.com/photo-1558857563-b371f30ca6a5",
            "description": "Signature brown sugar boba pearls with fresh creamy milk.",
        },
        {
            "name": "Lemon Iced Tea",
            "barcode": "884500129390",
            "category": "tea_milk",
            "price": 1.80,
            "cost_price": 0.50,
            "stock_qty": 160,
            "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc",
            "description": "Refreshing black tea infused with real lemon juice.",
        },
        {
            "name": "Fresh Butter Croissant",
            "barcode": "884500129391",
            "category": "bakery",
            "price": 1.50,
            "cost_price": 0.65,
            "stock_qty": 60,
            "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a",
            "description": "Golden, flaky, and buttery French bakery croissant.",
        },
        {
            "name": "Chocolate Chip Muffin",
            "barcode": "884500129392",
            "category": "bakery",
            "price": 1.75,
            "cost_price": 0.70,
            "stock_qty": 50,
            "image_url": "https://images.unsplash.com/photo-1607958996333-41aef7caefaa",
            "description": "Soft baked chocolate muffin with rich Belgian chocolate chips.",
        },
        {
            "name": "Strawberry Cheesecake",
            "barcode": "884500129393",
            "category": "bakery",
            "price": 3.50,
            "cost_price": 1.50,
            "stock_qty": 35,
            "image_url": "https://images.unsplash.com/photo-1565958011703-44f9829ba187",
            "description": "New York style cheesecake topped with fresh strawberry compote.",
        },
        {
            "name": "Mineral Water 500ml",
            "barcode": "884500129394",
            "category": "beverages",
            "price": 0.75,
            "cost_price": 0.25,
            "stock_qty": 250,
            "image_url": "https://images.unsplash.com/photo-1559839914-17aae19cec71",
            "description": "Purified chilled drinking water.",
        },
        {
            "name": "Fresh Orange Juice",
            "barcode": "884500129395",
            "category": "beverages",
            "price": 2.50,
            "cost_price": 0.90,
            "stock_qty": 80,
            "image_url": "https://images.unsplash.com/photo-1613478223719-2ab802602423",
            "description": "100% freshly squeezed orange juice with no added sugar.",
        },
    ]

    for p_item in products_data:
        existing_prod = db.query(Product).filter(
            Product.store_id == store1.id,
            Product.barcode == p_item["barcode"],
        ).first()
        if not existing_prod:
            new_prod = Product(
                store_id=store1.id,
                name=p_item["name"],
                barcode=p_item["barcode"],
                category=p_item["category"],
                category_id=cat_map.get(p_item["category"]),
                price=p_item["price"],
                cost_price=p_item["cost_price"],
                stock_qty=p_item["stock_qty"],
                image_url=p_item["image_url"],
                description=p_item["description"],
                is_active=True,
            )
            db.add(new_prod)

    # 5. Seed Store 1 Customers
    if not db.query(Customer).filter(Customer.store_id == store1.id).first():
        customers_data = [
            {"name": "Sok Vannak", "phone": "012 345 678", "email": "vannak@gmail.com", "points": 120, "orders": 14, "spent": 48.50},
            {"name": "Chan Bopha", "phone": "098 765 432", "email": "bopha@gmail.com", "points": 85, "orders": 9, "spent": 32.00},
            {"name": "Keo Socheat", "phone": "087 112 233", "email": "socheat@gmail.com", "points": 210, "orders": 22, "spent": 76.50},
        ]
        for c in customers_data:
            cust = Customer(
                store_id=store1.id,
                name=c["name"],
                phone=c["phone"],
                email=c["email"],
                points=c["points"],
                total_orders=c["orders"],
                total_spent=c["spent"],
            )
            db.add(cust)

    # 6. Seed Store 1 Suppliers
    if not db.query(Supplier).filter(Supplier.store_id == store1.id).first():
        suppliers_data = [
            {"name": "Mondulkiri Coffee Roasters", "company": "Mondulkiri Farm Co., Ltd", "phone": "023 888 111", "category": "Coffee Beans"},
            {"name": "Anchor Dairy Cambodia", "company": "Fonterra Brands", "phone": "023 777 222", "category": "Dairy & Milk"},
            {"name": "Phnom Penh Bakery Supplies", "company": "PP Bakery Supply", "phone": "023 666 333", "category": "Flour, Yeast & Packaging"},
        ]
        for s in suppliers_data:
            sup = Supplier(
                store_id=store1.id,
                name=s["name"],
                company_name=s["company"],
                phone=s["phone"],
                category=s["category"],
            )
            db.add(sup)

    # 7. Seed Store 1 Expenses
    if not db.query(Expense).filter(Expense.store_id == store1.id).first():
        now = datetime.now(timezone.utc)
        expenses_data = [
            {"title": "Electric Bill (EDC Store)", "category": "Utilities", "amount": 5.50, "date": now},
            {"title": "Water Utility (PPWSA)", "category": "Utilities", "amount": 2.50, "date": now},
            {"title": "Store Napkins & Cups Restock", "category": "Supplies", "amount": 12.00, "date": now - timedelta(days=1)},
        ]
        for e in expenses_data:
            exp = Expense(
                store_id=store1.id,
                title=e["title"],
                category=e["category"],
                amount=e["amount"],
                date=e["date"],
                recorded_by="Prak Panha",
            )
            db.add(exp)

    # 8. Seed Store 1 Sales (Invoices)
    if not db.query(Sale).filter(Sale.store_id == store1.id).first():
        now = datetime.now(timezone.utc)
        demo_sales = [
            {
                "invoice": f"INV-{now.strftime('%Y%m%d')}-0001",
                "customer": "Sok Vannak",
                "phone": "012 345 678",
                "method": "ABA_KHQR",
                "total": 5.25,
                "date": now - timedelta(hours=3),
                "items": [
                    {"name": "Caramel Macchiato", "qty": 1, "price": 2.75},
                    {"name": "Hot Cappuccino", "qty": 1, "price": 2.50},
                ],
            },
            {
                "invoice": f"INV-{now.strftime('%Y%m%d')}-0002",
                "customer": "Chan Bopha",
                "phone": "098 765 432",
                "method": "CASH",
                "total": 5.80,
                "date": now - timedelta(hours=2),
                "items": [
                    {"name": "Brown Sugar Pearl Milk Tea", "qty": 1, "price": 2.80},
                    {"name": "Matcha Green Tea Latte", "qty": 1, "price": 3.00},
                ],
            },
            {
                "invoice": f"INV-{now.strftime('%Y%m%d')}-0003",
                "customer": "General Customer",
                "phone": None,
                "method": "CASH",
                "total": 3.50,
                "date": now - timedelta(hours=1),
                "items": [
                    {"name": "Iced Americano", "qty": 1, "price": 2.00},
                    {"name": "Fresh Butter Croissant", "qty": 1, "price": 1.50},
                ],
            },
        ]

        for s in demo_sales:
            sale = Sale(
                store_id=store1.id,
                invoice_no=s["invoice"],
                cashier_name="Prak Panha",
                customer_name=s["customer"],
                customer_phone=s["phone"],
                subtotal=s["total"],
                discount=0.0,
                tax=0.0,
                total_amount=s["total"],
                payment_method=s["method"],
                payment_status="PAID",
                created_at=s["date"],
                items=[
                    SaleItem(
                        product_name=it["name"],
                        unit_price=it["price"],
                        quantity=it["qty"],
                        total_price=it["price"] * it["qty"],
                    )
                    for it in s["items"]
                ],
            )
            db.add(sale)

    # 9. Seed Store 2 (AudiCafe - Toul Kork Branch for multi-store demonstration)
    store2 = db.query(Store).filter(Store.store_code == "STORE-002").first()
    if not store2:
        store2 = Store(
            store_code="STORE-002",
            store_name="AudiCafe - Toul Kork",
            store_branch="Toul Kork Branch",
            phone_number="078 111 222",
            email="toulkork@audicafe.com",
            address="St. 315, Toul Kork, Phnom Penh",
            currency_symbol="$",
            exchange_rate_khr=4100.0,
            is_active=True,
        )
        db.add(store2)
        db.flush()

        # Store 2 Settings
        setting2 = StoreSetting(
            store_id=store2.id,
            printer_name="Bluetooth 80mm POS Thermal",
            printer_paper_width=80,
            auto_print_receipt=True,
            sound_alert=True,
            receipt_header="Welcome to AudiCafe (Toul Kork)",
            receipt_footer="Thank you! Visit us again.",
        )
        db.add(setting2)

        # Store 2 Admin
        admin2 = User(
            store_id=store2.id,
            full_name="Rithy Dara",
            phone_number="078 111 222",
            email="toulkork@audicafe.com",
            hashed_password=get_password_hash("123456"),
            pin_code="1111",
            role="store_admin",
            shift="Full-Time",
            telegram_username="@audicafe_tk",
            avatar_index=2,
            is_active=True,
        )
        db.add(admin2)
        db.flush()

        # Seed Store 2 StoreOwner record
        owner2 = StoreOwner(
            user_id=admin2.id,
            store_id=store2.id,
            status="approved",
            business_type="Coffee & Bakery",
            business_license="BL-2026-TK02",
            approved_at=datetime.now(timezone.utc),
        )
        db.add(owner2)
        db.flush()

        # Store 2 Cashier
        cashier2 = User(
            store_id=store2.id,
            full_name="Bopha Meas",
            phone_number="078 333 444",
            email="bopha.meas@audicafe.com",
            hashed_password=get_password_hash("123456"),
            pin_code="2222",
            role="cashier",
            shift="Afternoon Shift",
            telegram_username="@bopha_pos",
            avatar_index=3,
            is_active=True,
        )
        db.add(cashier2)
        db.flush()

        # Seed Store 2 StaffLink record in staffs_link
        link2 = StaffLink(
            store_owner_id=owner2.id,
            store_id=store2.id,
            staff_user_id=cashier2.id,
            role_title="Cashier",
            permissions='["pos_sales", "discount"]',
            is_active=True,
        )
        db.add(link2)

        # Store 2 Categories & Sample Products
        cat_tk = Category(store_id=store2.id, name="Coffee", code="coffee", icon="local_cafe")
        db.add(cat_tk)
        db.flush()

        prod_tk = Product(
            store_id=store2.id,
            name="Signature TK Cold Brew",
            barcode="884500888001",
            category="coffee",
            category_id=cat_tk.id,
            price=3.00,
            cost_price=1.20,
            stock_qty=80,
            is_active=True,
        )
        db.add(prod_tk)

    # 10. Seed Sample Pending Store Owner Application for Administrator Verification/Approval
    pending_user = db.query(User).filter(User.phone_number == "097 888 123").first()
    if not pending_user:
        pending_store = Store(
            store_code="STORE-003",
            store_name="AudiCafe Express Sihanoukville",
            store_branch="Ochheuteal Beach Outlet (SHV04)",
            phone_number="097 888 123",
            email="vicheka.keo@audicafe.com",
            address="2 Thnou St, Sangkat 4, Preah Sihanouk",
            currency_symbol="$",
            exchange_rate_khr=4100.0,
            is_active=False,  # inactive until approved by Administrator
        )
        db.add(pending_store)
        db.flush()

        pending_user = User(
            store_id=pending_store.id,
            full_name="Vicheka Keo",
            phone_number="097 888 123",
            email="vicheka.keo@audicafe.com",
            hashed_password=get_password_hash("123456"),
            pin_code="8888",
            role="store_admin",
            shift="Store Owner",
            avatar_index=4,
            is_active=False,  # inactive until approved by Administrator
        )
        db.add(pending_user)
        db.flush()

        pending_owner = StoreOwner(
            user_id=pending_user.id,
            store_id=pending_store.id,
            status="pending",
            business_type="Cafe & Beverage Bar",
            business_license="BL-2026-SHV04",
        )
        db.add(pending_owner)

    db.commit()
