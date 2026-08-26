# KITLUY SaaS POS & Multi-Tenant Engine (sever_prak)

Multi-tenant **SaaS** POS Engine with a 3-tier Role Hierarchy built in FastAPI:

```
👑 Level 1: Administrator (Platform Super Admin)
   │
   ├── Can Add Store Owners & Stores directly
   ├── Can Approve / Reject Store Owner applications (with reason)
   ├── Can Suspend / Activate any Store Owner & Store
   └── Global SaaS analytics, stores & tenant management
   │
   ▼
🏪 Level 2: Store Owner (Store Admin / Tenant)
   │
   ├── Manages their specific store profile & settings
   ├── Full control over store inventory, products, categories, pricing, expenses, reports
   └── Can Add, Link, and Manage their Staff (via `staffs_link`)
   │
   ▼
☕ Level 3: Staff (Cashier, Barista, Inventory Keeper)
   │
   ├── Linked to Store & Store Owner via `staffs_link`
   ├── POS sales, barcode scanning, checkout, and receipt generation
   └── Quick 4-digit PIN terminal login
```

---

## 🗄️ Database Tables Architecture

1. **`store_owners` (`Store_owner`)**:
   - `id`: Primary key
   - `user_id`: Foreign key -> `users.id`
   - `store_id`: Foreign key -> `stores.id`
   - `status`: `pending`, `approved`, `rejected`, `active`, `suspended`
   - `business_type`: e.g. "Cafe & Beverage", "Retail", "Bakery"
   - `business_license`: License / registration reference
   - `rejection_reason`: Explanation if application rejected by Administrator
   - `approved_by`: Administrator ID (`users.id`)
   - `approved_at`: Timestamp

2. **`staffs_link`**:
   - `id`: Primary key
   - `store_owner_id`: Foreign key -> `store_owners.id`
   - `store_id`: Foreign key -> `stores.id`
   - `staff_user_id`: Foreign key -> `users.id`
   - `role_title`: `Cashier`, `Barista`, `Inventory / Stock`, `Supervisor`
   - `permissions`: JSON array (e.g. `["pos_sales", "discount", "reports", "stock_edit"]`)
   - `is_active`: Boolean status

---

## 🔑 Default Seeded Accounts

| Role | Name | Phone Number | Password | Quick PIN | Store Access |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 👑 **Administrator** | Platform Owner | `071 00 00 000` | `admin123` | `9999` | **All Stores & Platform Owner** |
| 🏪 **Store Owner 1** | Prak Panha | `071 93 93 991` | `123456` | `1234` | **Store 1** (AudiCafe Main Branch) |
| ☕ **Staff 1** | Sophea Sok | `012 888 999` | `123456` | `0000` | **Store 1** (AudiCafe Main Branch) |
| 🏪 **Store Owner 2** | Rithy Dara | `078 111 222` | `123456` | `1111` | **Store 2** (AudiCafe Toul Kork) |
| ☕ **Staff 2** | Bopha Meas | `078 333 444` | `123456` | `2222` | **Store 2** (AudiCafe Toul Kork) |

---

## 🏛️ SaaS Role Permissions & Endpoints

### 1. Administrator (`super_admin`)
- **Dashboard & Revenue**: `GET /api/v1/admin/dashboard`
- **Store Owners Management**:
  - `GET /api/v1/admin/store-owners` (filter by status: `pending`, `approved`, `rejected`)
  - `POST /api/v1/admin/store-owners` (create store owner + store)
  - `POST /api/v1/admin/store-owners/{id}/approve` (approve store owner)
  - `POST /api/v1/admin/store-owners/{id}/reject` (reject store owner with reason)
  - `DELETE /api/v1/admin/store-owners/{id}` (suspend store owner)
- **Stores Management**: `GET, POST, PUT, DELETE /api/v1/admin/stores`

### 2. Store Owner (`store_admin` / `store_owner`)
- **Staff Management** (linked via `staffs_link`):
  - `GET /api/v1/staff`: List all staff in store
  - `POST /api/v1/staff`: Add new staff (Cashiers, Baristas, Stock Staff)
  - `PUT /api/v1/staff/{id}`: Update staff shift, role, avatar, PIN, permissions
  - `DELETE /api/v1/staff/{id}`: Deactivate staff member
- **Store Operations**:
  - Full CRUD on products, categories, stock counts, barcodes, expenses, and sales reports.

### 3. Staff (`cashier` / `barista`)
- POS Checkout with automatic stock deduction (`POST /api/v1/sales/checkout`)
- Quick 4-digit PIN access on POS terminals (`POST /api/v1/auth/pin-login`)
- Barcode scanning & live catalog search within their store

---

## 🧪 Run Automated Tests
```bash
python -m pytest
```

---

## 🚀 Run Dev Server
```bash
python run.py
```
- **Swagger UI**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- **ReDoc**: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)
