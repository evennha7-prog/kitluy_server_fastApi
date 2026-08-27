from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.utils.seed_data import seed_initial_data
from app.routers import (
    admin_router,
    auth_router,
    categories_router,
    products_router,
    sales_router,
    analytics_router,
    customers_router,
    suppliers_router,
    expenses_router,
    purchases_router,
    settings_router,
    staff_router,
    invoice_templates_router,
)


def _run_auto_migrations():
    """Auto-migrate schema columns for existing database tables to ensure tenant_id across all tables."""
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
        "user_invoice_templates",
    ]
    with engine.connect() as conn:
        # 1. Add color and category_id to products if missing
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN color VARCHAR(50) DEFAULT '#2E7D32';"))
            conn.commit()
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN category_id INT NULL;"))
            conn.commit()
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN telegram_username VARCHAR(100) NULL;"))
            conn.commit()
        except Exception:
            pass


        # 2. Add tenant_id to all tenant-scoped tables
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

        # 3. Add store_id & tenant_id to sale_items and purchase_items
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

        # 4. Add tenant_id to stores table
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create tables and seed initial data safely
    try:
        Base.metadata.create_all(bind=engine)
        _run_auto_migrations()
        
        db = SessionLocal()
        try:
            seed_initial_data(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[Warning] Database initialization during startup skipped or failed: {e}")
    
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(categories_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(sales_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(suppliers_router, prefix=settings.API_V1_STR)
app.include_router(expenses_router, prefix=settings.API_V1_STR)
app.include_router(purchases_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(staff_router, prefix=settings.API_V1_STR)
app.include_router(invoice_templates_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "architecture": "Multi-Tenant SaaS (Super Admin -> Store Admins -> Staff)",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
