"""
Database Migration and Seeding Script for KITLUY SaaS POS Engine.
Run this script to initialize, migrate, and seed the database.
Usage: python migrate.py [--reset]
"""

import sys
import sqlalchemy
from sqlalchemy import text
from app.core.database import Base, engine, SessionLocal
from app.models import (
    Store,
    User,
    StoreOwner,
    StaffLink,
    Product,
    Category,
    Sale,
    SaleItem,
    Customer,
    Supplier,
    Expense,
    Purchase,
    PurchaseItem,
    StoreSetting,
)
from app.utils.seed_data import seed_initial_data


def run_migration(reset: bool = False):
    print("[*] Connecting to database:", engine.url)
    
    with engine.connect() as conn:
        if reset:
            print("[!] Resetting database (dropping existing tables)...")
            is_mysql = "mysql" in str(engine.url)
            if is_mysql:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                # Get all tables and drop them directly
                result = conn.execute(text("SHOW TABLES;"))
                tables = [r[0] for r in result.fetchall()]
                for t in tables:
                    print(f"  - Dropping table `{t}`...")
                    conn.execute(text(f"DROP TABLE IF EXISTS `{t}`;"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                conn.commit()
            else:
                Base.metadata.drop_all(bind=conn)
                conn.commit()

        print("[+] Creating all database tables with SaaS Multi-Tenant schema...")
        Base.metadata.create_all(bind=conn)
        conn.commit()

        print("[+] Ensuring `tenant_id` column exists across all database tables...")
        tenant_tables = [
            "users",
            "store_owners",
            "staffs_link",
            "products",
            "categories",
            "sales",
            "customers",
            "suppliers",
            "expenses",
            "purchases",
            "store_settings",
        ]
        for table in tenant_tables:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN tenant_id INT NULL;"))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text(f"UPDATE {table} SET tenant_id = store_id WHERE tenant_id IS NULL AND store_id IS NOT NULL;"))
                conn.commit()
            except Exception:
                pass

        for item_table, parent_table, fk_col in [("sale_items", "sales", "sale_id"), ("purchase_items", "purchases", "purchase_id")]:
            try:
                conn.execute(text(f"ALTER TABLE {item_table} ADD COLUMN store_id INT NULL;"))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text(f"ALTER TABLE {item_table} ADD COLUMN tenant_id INT NULL;"))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text(f"UPDATE {item_table} it JOIN {parent_table} p ON it.{fk_col} = p.id SET it.store_id = p.store_id, it.tenant_id = p.store_id WHERE it.tenant_id IS NULL;"))
                conn.commit()
            except Exception:
                pass

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN telegram_username VARCHAR(100) NULL;"))
            conn.commit()
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE stores ADD COLUMN tenant_id VARCHAR(50) NULL;"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("UPDATE stores SET tenant_id = store_code WHERE tenant_id IS NULL;"))
            conn.commit()
        except Exception:
            pass
    
    inspector = sqlalchemy.inspect(engine)
    tables = inspector.get_table_names()
    print(f"[OK] Verified {len(tables)} tables in database: {', '.join(tables)}")

    print("[*] Seeding initial stores, admins, products, and catalog data...")
    db = SessionLocal()
    try:
        seed_initial_data(db)
        print("[DONE] Database migration and seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    run_migration(reset=reset_flag)
