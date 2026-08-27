import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_store_admin, get_password_hash
from app.models.user import User
from app.models.store_owner import StoreOwner
from app.models.staff_link import StaffLink
from app.repositories.user_repository import UserRepository
from app.schemas.user import StaffCreate, UserUpdate, UserResponse
from app.schemas.staff_link import StaffLinkCreate, StaffLinkUpdate, StaffLinkResponse

router = APIRouter(prefix="/staff", tags=["Staff Management (Store Owner)"])


@router.get("", response_model=List[StaffLinkResponse])
def list_staff(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    """
    Store Owner lists all staff members linked to their store via staffs_link.
    Super Admin lists across all stores.
    """
    query = db.query(StaffLink)
    if current_admin.role != "super_admin":
        query = query.filter(StaffLink.store_id == current_admin.store_id)

    links = query.order_by(StaffLink.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for l in links:
        u = l.staff_user
        results.append(
            StaffLinkResponse(
                id=l.id,
                store_owner_id=l.store_owner_id,
                store_id=l.store_id,
                staff_user_id=l.staff_user_id,
                role_title=l.role_title,
                permissions=l.permissions or '["pos_sales", "discount"]',
                is_active=l.is_active,
                created_at=l.created_at,
                updated_at=l.updated_at,
                full_name=u.full_name if u else "Staff Member",
                phone_number=u.phone_number if u else "",
                email=u.email if u else None,
                pin_code=u.pin_code if u else "0000",
                shift=u.shift if u else "Morning Shift",
                avatar_index=u.avatar_index if u else 0,
                store_name=l.store.store_name if l.store else None,
            )
        )
    return results


@router.post("", response_model=StaffLinkResponse)
def create_staff(
    staff_in: StaffLinkCreate,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    """
    Store Owner adds a new Staff member, creates a User account, and links them via staffs_link.
    """
    repo = UserRepository(db)
    clean_phone = staff_in.phone_number.replace(" ", "").replace("-", "")
    if repo.get_by_phone(staff_in.phone_number) or repo.get_by_phone(clean_phone):
        raise HTTPException(status_code=400, detail="Phone number already registered")

    if staff_in.email and repo.get_by_email(staff_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    store_id = current_admin.store_id or 1

    # Find store owner record for this store
    store_owner = db.query(StoreOwner).filter(StoreOwner.store_id == store_id).first()
    if not store_owner:
        # Fallback to current admin's store owner record or create on the fly
        store_owner = StoreOwner(
            user_id=current_admin.id,
            store_id=store_id,
            tenant_id=store_id,
            status="approved",
            business_type="Cafe & Beverage",
        )
        db.add(store_owner)
        db.flush()

    # 1. Create Staff User
    raw_password = staff_in.password or "123456"
    hashed = get_password_hash(raw_password)
    user_role = "store_admin" if "manager" in (staff_in.role_title or "").lower() else "cashier"

    user = User(
        store_id=store_id,
        tenant_id=store_id,
        full_name=staff_in.full_name,
        phone_number=staff_in.phone_number,
        email=staff_in.email,
        hashed_password=hashed,
        pin_code=staff_in.pin_code or "0000",
        role=user_role,
        shift=staff_in.shift or "Morning Shift (06:30 AM - 03:00 PM)",
        avatar_index=staff_in.avatar_index,
        is_active=staff_in.is_active,
    )
    db.add(user)
    db.flush()

    # 2. Create StaffLink in staffs_link table
    staff_link = StaffLink(
        store_owner_id=store_owner.id,
        store_id=store_id,
        tenant_id=store_id,
        staff_user_id=user.id,
        role_title=staff_in.role_title or "Cashier",
        permissions=staff_in.permissions or '["pos_sales", "discount"]',
        is_active=staff_in.is_active,
    )
    db.add(staff_link)
    db.commit()
    db.refresh(staff_link)

    return StaffLinkResponse(
        id=staff_link.id,
        store_owner_id=staff_link.store_owner_id,
        store_id=staff_link.store_id,
        staff_user_id=staff_link.staff_user_id,
        role_title=staff_link.role_title,
        permissions=staff_link.permissions,
        is_active=staff_link.is_active,
        created_at=staff_link.created_at,
        updated_at=staff_link.updated_at,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        pin_code=user.pin_code,
        shift=user.shift,
        avatar_index=user.avatar_index,
        store_name=current_admin.store.store_name if current_admin.store else None,
    )


@router.put("/{link_id}", response_model=StaffLinkResponse)
def update_staff(
    link_id: int,
    staff_in: StaffLinkUpdate,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    """
    Store Owner updates staff member role, permissions, and status.
    """
    link = db.query(StaffLink).filter(StaffLink.id == link_id).first()
    if not link:
        # Fallback: maybe staff_user_id was passed instead of link_id
        link = db.query(StaffLink).filter(StaffLink.staff_user_id == link_id).first()

    if not link:
        raise HTTPException(status_code=404, detail="Staff record not found")

    if current_admin.role != "super_admin" and link.store_id != current_admin.store_id:
        raise HTTPException(status_code=403, detail="Access denied to staff in other stores")

    # Update Link
    if staff_in.role_title is not None:
        link.role_title = staff_in.role_title
    if staff_in.permissions is not None:
        link.permissions = staff_in.permissions
    if staff_in.is_active is not None:
        link.is_active = staff_in.is_active

    # Update User
    user = link.staff_user
    if user:
        if staff_in.shift is not None:
            user.shift = staff_in.shift
        if staff_in.pin_code is not None:
            user.pin_code = staff_in.pin_code
        if staff_in.avatar_index is not None:
            user.avatar_index = staff_in.avatar_index
        if staff_in.is_active is not None:
            user.is_active = staff_in.is_active

    db.commit()
    db.refresh(link)

    return StaffLinkResponse(
        id=link.id,
        store_owner_id=link.store_owner_id,
        store_id=link.store_id,
        staff_user_id=link.staff_user_id,
        role_title=link.role_title,
        permissions=link.permissions,
        is_active=link.is_active,
        created_at=link.created_at,
        updated_at=link.updated_at,
        full_name=user.full_name if user else "Staff",
        phone_number=user.phone_number if user else "",
        email=user.email if user else None,
        pin_code=user.pin_code if user else "0000",
        shift=user.shift if user else "",
        avatar_index=user.avatar_index if user else 0,
        store_name=link.store.store_name if link.store else None,
    )


@router.delete("/{link_id}")
def delete_staff(
    link_id: int,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    """
    Store Owner deactivates a linked staff member.
    """
    link = db.query(StaffLink).filter(StaffLink.id == link_id).first()
    if not link:
        link = db.query(StaffLink).filter(StaffLink.staff_user_id == link_id).first()

    if not link:
        raise HTTPException(status_code=404, detail="Staff record not found")

    if current_admin.role != "super_admin" and link.store_id != current_admin.store_id:
        raise HTTPException(status_code=403, detail="Access denied to staff in other stores")

    link.is_active = False
    if link.staff_user:
        link.staff_user.is_active = False

    db.commit()
    return {"message": f"Staff member '{link.staff_user.full_name if link.staff_user else link_id}' deactivated"}
