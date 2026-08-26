# KITLUY SaaS POS & Inventory Backend (sever_prak)

Multi-tenant **SaaS** POS Engine with a 3-tier Role Hierarchy built in FastAPI:

```
Platform Super Administrator (1 Owner)
  │
  ├── Store Admin 1 (Store 1) ─── Staff / Cashiers
  ├── Store Admin 2 (Store 2) ─── Staff / Cashiers
  ├── Store Admin 3 (Store 3) ─── Staff / Cashiers
  └── Store Admin N (Store N) ─── ...
```

---

## 🔑 Default Seeded Accounts

| Role | Name | Phone Number | Password | Quick PIN | Store Access |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | Platform Owner | `071 00 00 000` | `admin123` | `9999` | **All Stores & Platform** |
| **Store Admin 1** | Prak Panha | `071 93 93 991` | `123456` | `1234` | **Store 1** (AudiCafe Main) |
| **Cashier 1** | Sophea Sok | `012 888 999` | `123456` | `0000` | **Store 1** (AudiCafe Main) |
| **Store Admin 2** | Rithy Dara | `078 111 222` | `123456` | `1111` | **Store 2** (AudiCafe Toul Kork) |
| **Cashier 2** | Bopha Meas | `078 333 444` | `123456` | `2222` | **Store 2** (AudiCafe Toul Kork) |

---

## 🏛️ SaaS Role Permissions & Logical Hierarchy

### 1. Super Administrator (`super_admin`)
- Full platform management: View global platform revenue, active stores count, and user totals (`GET /api/v1/admin/dashboard`).
- Create new stores (`POST /api/v1/admin/stores`).
- List and inspect all stores with live revenue/staff stats (`GET /api/v1/admin/stores`).
- Deactivate / activate any store (`DELETE /api/v1/admin/stores/{id}`).
- View staff members across any store (`GET /api/v1/admin/stores/{id}/staff`).

### 2. Store Administrator (`store_admin`)
- Owns and manages their specific store (`Store 1, Store 2, Store 3...`).
- **Staff Management**:
  - `GET /api/v1/staff`: List all staff in their store.
  - `POST /api/v1/staff`: Add new staff (Cashiers, Baristas, Stock Staff) directly to their store.
  - `PUT /api/v1/staff/{id}`: Update staff shift, role, avatar, PIN code.
  - `DELETE /api/v1/staff/{id}`: Deactivate staff member.
- **Store Operations**:
  - Full CRUD on their store's products, categories, stock quantities, and barcodes.
  - View real-time store analytics, profit/loss, daily trends.
  - Manage store expenses, purchases, customers, and suppliers.
  - Configure receipt printer header, paper width (80mm), and Telegram alerts.

### 3. Store Staff / Cashier (`cashier`)
- POS Checkout with automatic stock deduction and invoice generation (`POST /api/v1/sales/checkout`).
- Quick 4-digit PIN access on POS terminals (`POST /api/v1/auth/pin-login`).
- Barcode scanning & live catalog search within their store.

---

## 🚀 SaaS Registration Flow (`POST /api/v1/auth/register-store`)

New store owners can register on the platform in a single API call:
```json
{
  "store_name": "My New Coffee Shop",
  "store_branch": "BKK1 Branch",
  "address": "Phnom Penh, Cambodia",
  "admin_name": "Store Owner Name",
  "phone_number": "010 123 456",
  "password": "password123",
  "pin_code": "1234"
}
```
This automatically creates:
1. A new `Store` tenant record.
2. A new `StoreSetting` configuration for receipt & thermal printing.
3. Default `Categories` (Coffee, Tea & Milk, Bakery, Beverages).
4. The `store_admin` account linked to the new store.

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
