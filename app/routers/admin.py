from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_super_admin, get_optional_current_user, get_password_hash
from app.models.user import User
from app.models.store import Store
from app.models.store_owner import StoreOwner
from app.models.staff_link import StaffLink
from app.repositories.user_repository import UserRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.sale_repository import SaleRepository
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreWithStatsResponse
from app.schemas.store_owner import (
    StoreOwnerCreate,
    StoreOwnerRegister,
    StoreOwnerApproval,
    StoreOwnerUpdate,
    StoreOwnerResponse,
)
from app.schemas.user import UserResponse
from app.services.store_service import StoreService

router = APIRouter(prefix="/admin", tags=["Super Administrator (Platform Owner)"])


@router.get("/dashboard")
def get_super_admin_dashboard(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    store_repo = StoreRepository(db)
    user_repo = UserRepository(db)
    stores = store_repo.list_all(limit=1000)
    
    total_stores = len(stores)
    active_stores = sum(1 for s in stores if s.is_active)
    total_users = len(user_repo.list_all(limit=5000))
    
    # Store owners count and pending applications
    total_owners = db.query(StoreOwner).count()
    pending_owners = db.query(StoreOwner).filter(StoreOwner.status == "pending").count()
    approved_owners = db.query(StoreOwner).filter(StoreOwner.status == "approved").count()
    total_staff_links = db.query(StaffLink).count()

    # Calculate total platform volume
    total_platform_revenue = 0.0
    for s in stores:
        stats = store_repo.get_store_stats(s.id)
        total_platform_revenue += stats["total_revenue"]

    return {
        "platform_name": "KITLUY SaaS POS Engine",
        "super_admin": current_user.full_name,
        "total_stores": total_stores,
        "active_stores": active_stores,
        "total_users": total_users,
        "total_store_owners": total_owners,
        "pending_store_owners": pending_owners,
        "approved_store_owners": approved_owners,
        "total_staff_links": total_staff_links,
        "total_platform_revenue": round(total_platform_revenue, 2),
    }


# ==========================================
# Store Owner Management (Administrator)
# ==========================================

@router.get("/store-owners", response_model=List[StoreOwnerResponse])
def list_store_owners(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: pending, approved, rejected, active, suspended"),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Administrator lists all Store Owners with tenancy and status details.
    Auto-discovers and links any registered store owner users.
    """
    try:
        # Auto-discover and link any registered store owner users not yet in store_owners table
        unlinked_users = db.query(User).filter(
            (User.role.in_(["store_admin", "store_owner"])) | (User.is_active == False)
        ).all()
        for u in unlinked_users:
            if u.role == "super_admin":
                continue
            existing = db.query(StoreOwner).filter(StoreOwner.user_id == u.id).first()
            if not existing:
                store_id = u.store_id
                if not store_id:
                    new_store = Store(
                        store_code=f"STORE-{u.id:03d}",
                        store_name=f"{u.full_name}'s Store",
                        store_branch="Main Branch",
                        phone_number=u.phone_number,
                        email=u.email,
                        is_active=u.is_active,
                    )
                    db.add(new_store)
                    db.flush()
                    u.store_id = new_store.id
                    u.tenant_id = new_store.id
                    store_id = new_store.id

                new_owner = StoreOwner(
                    user_id=u.id,
                    store_id=store_id,
                    tenant_id=store_id,
                    status="pending" if not u.is_active else "approved",
                    business_type="Retail & Business",
                )
                db.add(new_owner)
        db.commit()
    except Exception:
        db.rollback()

    query = db.query(StoreOwner)
    if status_filter and status_filter.lower() != "all":
        query = query.filter(StoreOwner.status == status_filter.lower())

    owners = query.order_by(StoreOwner.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for o in owners:
        staff_count = db.query(StaffLink).filter(StaffLink.store_owner_id == o.id, StaffLink.is_active == True).count()
        results.append(
            StoreOwnerResponse(
                id=o.id,
                user_id=o.user_id,
                store_id=o.store_id,
                status=o.status,
                business_type=o.business_type,
                business_license=o.business_license,
                rejection_reason=o.rejection_reason,
                approved_by=o.approved_by,
                approved_at=o.approved_at,
                created_at=o.created_at,
                updated_at=o.updated_at,
                owner_name=o.user.full_name if o.user else None,
                owner_phone=o.user.phone_number if o.user else None,
                owner_email=o.user.email if o.user else None,
                owner_telegram=o.user.telegram_username if o.user else None,
                store_name=o.store.store_name if o.store else None,
                store_branch=o.store.store_branch if o.store else None,
                address=o.store.address if o.store else None,
                staff_count=staff_count,
            )
        )
    return results


@router.post("/store-owners", response_model=StoreOwnerResponse)
def create_store_owner(
    req: StoreOwnerRegister,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Administrator directly registers a new Store Owner and provisions their Store.
    """
    user_repo = UserRepository(db)
    if user_repo.get_by_phone(req.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    if req.email and user_repo.get_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # 1. Create store
    store_service = StoreService(db)
    store_code = f"STORE-{datetime.now().strftime('%m%d%H%M%S')}"
    store = store_service.create_store(
        StoreCreate(
            store_name=req.store_name,
            store_branch=req.store_branch or "Main Branch",
            store_code=store_code,
            address=req.address,
        )
    )

    # 2. Create Store Owner user
    hashed = get_password_hash(req.password)
    user = User(
        store_id=store.id,
        full_name=req.full_name,
        phone_number=req.phone_number,
        email=req.email,
        hashed_password=hashed,
        pin_code=req.pin_code or "1234",
        role="store_admin",
        shift="Store Owner / Manager",
        is_active=True,
    )
    db.add(user)
    db.flush()

    # 3. Create StoreOwner record in store_owners table
    owner = StoreOwner(
        user_id=user.id,
        store_id=store.id,
        status="approved",
        business_type=req.business_type or "Cafe & Beverage",
        business_license=req.business_license,
        approved_by=current_user.id,
        approved_at=datetime.now(timezone.utc),
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    return StoreOwnerResponse(
        id=owner.id,
        user_id=owner.user_id,
        store_id=owner.store_id,
        status=owner.status,
        business_type=owner.business_type,
        business_license=owner.business_license,
        approved_by=owner.approved_by,
        approved_at=owner.approved_at,
        created_at=owner.created_at,
        updated_at=owner.updated_at,
        owner_name=user.full_name,
        owner_phone=user.phone_number,
        owner_email=user.email,
        store_name=store.store_name,
        store_branch=store.store_branch,
        staff_count=0,
    )


@router.post("/store-owners/{owner_id}/approve", response_model=StoreOwnerResponse)
def approve_store_owner(
    owner_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Administrator approves a pending Store Owner application and activates their tenant store.
    """
    owner = db.query(StoreOwner).filter(StoreOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Store Owner application not found")

    owner.status = "approved"
    owner.rejection_reason = None
    owner.approved_by = current_user.id if current_user else 1
    owner.approved_at = datetime.now(timezone.utc)

    # Activate linked user and store
    if owner.user:
        owner.user.is_active = True
    if owner.store:
        owner.store.is_active = True

    db.commit()
    db.refresh(owner)

    staff_count = db.query(StaffLink).filter(StaffLink.store_owner_id == owner.id, StaffLink.is_active == True).count()
    return StoreOwnerResponse(
        id=owner.id,
        user_id=owner.user_id,
        store_id=owner.store_id,
        status=owner.status,
        business_type=owner.business_type,
        business_license=owner.business_license,
        rejection_reason=owner.rejection_reason,
        approved_by=owner.approved_by,
        approved_at=owner.approved_at,
        created_at=owner.created_at,
        updated_at=owner.updated_at,
        owner_name=owner.user.full_name if owner.user else None,
        owner_phone=owner.user.phone_number if owner.user else None,
        owner_email=owner.user.email if owner.user else None,
        owner_telegram=owner.user.telegram_username if owner.user else None,
        store_name=owner.store.store_name if owner.store else None,
        store_branch=owner.store.store_branch if owner.store else None,
        address=owner.store.address if owner.store else None,
        staff_count=staff_count,
    )


@router.post("/store-owners/{owner_id}/reject", response_model=StoreOwnerResponse)
def reject_store_owner(
    owner_id: int,
    payload: StoreOwnerApproval,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Administrator rejects a Store Owner application with an explanation reason.
    """
    owner = db.query(StoreOwner).filter(StoreOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Store Owner application not found")

    owner.status = "rejected"
    owner.rejection_reason = payload.rejection_reason or "Application did not meet platform verification standards"
    owner.approved_by = current_user.id if current_user else 1
    owner.approved_at = datetime.now(timezone.utc)

    # Deactivate linked user and store
    if owner.user:
        owner.user.is_active = False
    if owner.store:
        owner.store.is_active = False

    db.commit()
    db.refresh(owner)

    staff_count = db.query(StaffLink).filter(StaffLink.store_owner_id == owner.id, StaffLink.is_active == True).count()
    return StoreOwnerResponse(
        id=owner.id,
        user_id=owner.user_id,
        store_id=owner.store_id,
        status=owner.status,
        business_type=owner.business_type,
        business_license=owner.business_license,
        rejection_reason=owner.rejection_reason,
        approved_by=owner.approved_by,
        approved_at=owner.approved_at,
        created_at=owner.created_at,
        updated_at=owner.updated_at,
        owner_name=owner.user.full_name if owner.user else None,
        owner_phone=owner.user.phone_number if owner.user else None,
        owner_email=owner.user.email if owner.user else None,
        owner_telegram=owner.user.telegram_username if owner.user else None,
        store_name=owner.store.store_name if owner.store else None,
        store_branch=owner.store.store_branch if owner.store else None,
        address=owner.store.address if owner.store else None,
        staff_count=staff_count,
    )


@router.delete("/store-owners/{owner_id}")
def delete_or_suspend_store_owner(
    owner_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Administrator suspends or deactivates a Store Owner account and linked store.
    """
    owner = db.query(StoreOwner).filter(StoreOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Store Owner not found")

    owner.status = "suspended"
    if owner.user:
        owner.user.is_active = False
    if owner.store:
        owner.store.is_active = False

    db.commit()
    return {"message": f"Store Owner '{owner.user.full_name if owner.user else owner_id}' suspended successfully"}


# ==========================================
# Store Management (Administrator)
# ==========================================

@router.get("/stores", response_model=List[StoreWithStatsResponse])
def list_stores(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.list_stores_with_stats(skip=skip, limit=limit)


@router.get("/stores/{store_id}", response_model=StoreWithStatsResponse)
def get_store(
    store_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.get_by_id(store_id)


@router.post("/stores", response_model=StoreResponse)
def create_store(
    store_in: StoreCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.create_store(store_in)


@router.put("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store_in: StoreUpdate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.update_store(store_id, store_in)


@router.delete("/stores/{store_id}")
def deactivate_store(
    store_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    service = StoreService(db)
    return service.deactivate_store(store_id)


@router.get("/stores/{store_id}/staff", response_model=List[UserResponse])
def get_store_staff(
    store_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    staff_members = user_repo.list_by_store(store_id)
    return [UserResponse.model_validate(u) for u in staff_members]
