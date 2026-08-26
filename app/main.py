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
)


def _run_auto_migrations():
    """Auto-migrate schema columns for existing database tables."""
    with engine.connect() as conn:
        # Check and add 'color' column to 'products' table
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN color VARCHAR(50) DEFAULT '#2E7D32';"))
            conn.commit()
        except Exception:
            pass

        # Check and add 'category_id' column to 'products' table
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN category_id INT NULL;"))
            conn.commit()
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create tables on startup
    Base.metadata.create_all(bind=engine)
    
    # 2. Auto-migrate schema updates
    _run_auto_migrations()
    
    # 3. Seed initial data
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    
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
