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
