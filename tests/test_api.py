import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.utils.seed_data import seed_initial_data
from app.main import app

# SQLite StaticPool in-memory shared across test connections
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

init_db = TestingSessionLocal()
seed_initial_data(init_db)
init_db.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_and_root():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "Multi-Tenant" in root_resp.json()["architecture"]


def test_super_admin_flow():
    # 1. Super Admin Login
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"identifier": "071 00 00 000", "password": "admin123"},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["role"] == "super_admin"
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Super Admin Dashboard
    dash_resp = client.get(f"{settings.API_V1_STR}/admin/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_stores"] >= 2
    assert dash_data["active_stores"] >= 2

    # 3. Super Admin list all stores
    stores_resp = client.get(f"{settings.API_V1_STR}/admin/stores", headers=headers)
    assert stores_resp.status_code == 200
    stores = stores_resp.json()
    assert len(stores) >= 2

    # 4. Super Admin creates a new Store (Store 3)
    new_store = {
        "store_name": "Angkor Coffee Roastery",
        "store_branch": "Siem Reap Central",
        "phone_number": "063 999 888",
        "email": "siemreap@angkorcoffee.com",
        "address": "Pub Street, Siem Reap",
    }
    create_store_resp = client.post(
        f"{settings.API_V1_STR}/admin/stores",
        json=new_store,
        headers=headers,
    )
    assert create_store_resp.status_code == 200
    assert create_store_resp.json()["store_name"] == "Angkor Coffee Roastery"


def test_store_admin_and_staff_management():
    # 1. Store Admin 1 Login (AudiCafe Main Branch)
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"identifier": "071 93 93 991", "password": "123456"},
    )
    assert login_resp.status_code == 200
    admin1_token = login_resp.json()["access_token"]
    admin1_headers = {"Authorization": f"Bearer {admin1_token}"}
    store1_id = login_resp.json()["store_id"]
    assert store1_id == 1

    # 2. Store Admin 1 lists staff (only sees Store 1 staff)
    staff_resp = client.get(f"{settings.API_V1_STR}/staff", headers=admin1_headers)
    assert staff_resp.status_code == 200
    staff_list = staff_resp.json()
    assert all(s["store_id"] == 1 for s in staff_list)

    # 3. Store Admin 1 adds a new Cashier to Store 1
    new_staff = {
        "full_name": "Kosal Chea",
        "phone_number": "099 777 666",
        "email": "kosal@audicafe.com",
        "password": "password123",
        "pin_code": "4321",
        "role": "cashier",
        "shift": "Evening Shift (03:00 PM - 10:00 PM)",
    }
    add_staff_resp = client.post(f"{settings.API_V1_STR}/staff", json=new_staff, headers=admin1_headers)
    assert add_staff_resp.status_code == 200
    created_staff = add_staff_resp.json()
    assert created_staff["full_name"] == "Kosal Chea"
    assert created_staff["store_id"] == 1

    # 4. Newly added cashier can login with PIN
    cashier_pin_resp = client.post(
        f"{settings.API_V1_STR}/auth/pin-login",
        json={"pin": "4321", "store_id": 1},
    )
    assert cashier_pin_resp.status_code == 200
    assert cashier_pin_resp.json()["user"]["full_name"] == "Kosal Chea"


def test_tenant_data_isolation():
    # Store Admin 1 Token (Store 1)
    login1 = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "071 93 93 991", "password": "123456"})
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Store Admin 2 Token (Store 2 - Toul Kork)
    login2 = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "078 111 222", "password": "123456"})
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Store 1 products
    prod1_resp = client.get(f"{settings.API_V1_STR}/products", headers=headers1)
    assert prod1_resp.status_code == 200
    store1_prods = prod1_resp.json()
    assert len(store1_prods) >= 10
    store1_names = [p["name"] for p in store1_prods]
    assert "Caramel Macchiato" in store1_names
    assert "Signature TK Cold Brew" not in store1_names

    # Store 2 products (isolated!)
    prod2_resp = client.get(f"{settings.API_V1_STR}/products", headers=headers2)
    assert prod2_resp.status_code == 200
    store2_prods = prod2_resp.json()
    store2_names = [p["name"] for p in store2_prods]
    assert "Signature TK Cold Brew" in store2_names
    assert "Caramel Macchiato" not in store2_names


def test_saas_store_registration_flow():
    # A new store owner registers via SaaS endpoint
    register_payload = {
        "store_name": "Brown Bakery & Coffee",
        "store_branch": "BKK1 Flagship",
        "address": "St. 51, BKK1, Phnom Penh",
        "admin_name": "Vireak Bun",
        "phone_number": "010 555 777",
        "email": "vireak@brownbakery.com",
        "password": "securepassword123",
        "pin_code": "8888",
    }
    resp = client.post(f"{settings.API_V1_STR}/auth/register-store", json=register_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "store_admin"
    assert data["store_name"] == "Brown Bakery & Coffee"
    assert "access_token" in data

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # The new store admin can immediately add products to their newly created store
    new_prod = {
        "name": "Artisan Croissant",
        "barcode": "884999111222",
        "category": "bakery",
        "price": 2.50,
        "cost_price": 0.90,
        "stock_qty": 40,
    }
    prod_resp = client.post(f"{settings.API_V1_STR}/products", json=new_prod, headers=headers)
    assert prod_resp.status_code == 200
    assert prod_resp.json()["name"] == "Artisan Croissant"


def test_sales_checkout_scoped():
    # Login as Store 1 Cashier
    login_resp = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "012 888 999", "password": "123456"})
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    checkout_payload = {
        "cashier_name": "Sophea Sok",
        "customer_name": "Loyal Customer",
        "payment_method": "ABA_KHQR",
        "items": [
            {
                "product_name": "Caramel Macchiato",
                "barcode": "884500129384",
                "unit_price": 2.75,
                "quantity": 1,
            }
        ],
    }
    response = client.post(f"{settings.API_V1_STR}/sales/checkout", json=checkout_payload, headers=headers)
    assert response.status_code == 200
    sale = response.json()
    assert sale["total_amount"] == 2.75
    assert sale["store_id"] == 1


def test_analytics_summary_scoped():
    # Login as Store 1 Admin
    login_resp = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "071 93 93 991", "password": "123456"})
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    response = client.get(f"{settings.API_V1_STR}/analytics/summary", headers=headers)
    assert response.status_code == 200
    summary = response.json()
    assert "income" in summary
    assert "expense" in summary
    assert "net_profit" in summary
    assert "total_transactions" in summary


def test_categories_crud():
    # Login as Store 1 Admin
    login_resp = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "071 93 93 991", "password": "123456"})
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # 1. Create Category
    new_cat = {
        "name": "Fresh Smoothies",
        "code": "smoothies_special",
        "icon": "smoothies",
    }
    cat_resp = client.post(f"{settings.API_V1_STR}/categories", json=new_cat, headers=headers)
    assert cat_resp.status_code == 200
    cat_data = cat_resp.json()
    assert cat_data["name"] == "Fresh Smoothies"
    cat_id = cat_data["id"]

    # 2. List Categories
    list_resp = client.get(f"{settings.API_V1_STR}/categories", headers=headers)
    assert list_resp.status_code == 200
    assert any(c["id"] == cat_id for c in list_resp.json())

    # 3. Delete Category
    del_resp = client.delete(f"{settings.API_V1_STR}/categories/{cat_id}", headers=headers)
    assert del_resp.status_code == 200


def test_store_settings_scoped():
    # Login as Store 1 Admin
    login_resp = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "071 93 93 991", "password": "123456"})
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    response = client.get(f"{settings.API_V1_STR}/settings", headers=headers)
    assert response.status_code == 200
    settings_data = response.json()
    assert settings_data["store_name"] == "AudiCafe"
    assert settings_data["store_id"] == 1


def test_store_owner_approval_and_staff_link():
    # 1. Login as Super Admin
    admin_login = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "071 00 00 000", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    # 2. List Store Owners
    owners_resp = client.get(f"{settings.API_V1_STR}/admin/store-owners", headers=admin_headers)
    assert owners_resp.status_code == 200
    owners = owners_resp.json()
    assert len(owners) >= 2

    # Check pending owners
    pending = [o for o in owners if o["status"] == "pending"]
    if pending:
        target_owner = pending[0]
        # 3. Super Admin Approves pending Store Owner
        app_resp = client.post(f"{settings.API_V1_STR}/admin/store-owners/{target_owner['id']}/approve", headers=admin_headers)
        assert app_resp.status_code == 200
        assert app_resp.json()["status"] == "approved"

    # 4. Store Admin 1 lists staff links in staffs_link table
    login1 = client.post(f"{settings.API_V1_STR}/auth/login", json={"identifier": "071 93 93 991", "password": "123456"})
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

    staff_links_resp = client.get(f"{settings.API_V1_STR}/staff", headers=headers1)
    assert staff_links_resp.status_code == 200
    links = staff_links_resp.json()
    assert len(links) >= 1
    assert "role_title" in links[0]
    assert "permissions" in links[0]

