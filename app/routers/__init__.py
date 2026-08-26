from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.routers.sales import router as sales_router
from app.routers.analytics import router as analytics_router
from app.routers.customers import router as customers_router
from app.routers.suppliers import router as suppliers_router
from app.routers.expenses import router as expenses_router
from app.routers.purchases import router as purchases_router
from app.routers.settings import router as settings_router
from app.routers.staff import router as staff_router

__all__ = [
    "admin_router",
    "auth_router",
    "categories_router",
    "products_router",
    "sales_router",
    "analytics_router",
    "customers_router",
    "suppliers_router",
    "expenses_router",
    "purchases_router",
    "settings_router",
    "staff_router",
]
