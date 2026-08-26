from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_store_admin, get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import StaffCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/staff", tags=["Staff Management (Store Admin)"])


@router.get("", response_model=List[UserResponse])
def list_staff(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    if current_admin.role == "super_admin":
        users = repo.list_all(skip=skip, limit=limit)
    else:
        users = repo.list_by_store(current_admin.store_id, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.post("", response_model=UserResponse)
def create_staff(
    staff_in: StaffCreate,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    if repo.get_by_phone(staff_in.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    if staff_in.email and repo.get_by_email(staff_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    store_id = current_admin.store_id or 1

    hashed = get_password_hash(staff_in.password)
    user = User(
        store_id=store_id,
        full_name=staff_in.full_name,
        phone_number=staff_in.phone_number,
        email=staff_in.email,
        hashed_password=hashed,
        pin_code=staff_in.pin_code,
        role=staff_in.role or "cashier",
        shift=staff_in.shift or "Morning Shift (06:30 AM - 03:00 PM)",
        avatar_index=staff_in.avatar_index or 0,
        is_active=True,
    )
    created = repo.create(user)
    return UserResponse.model_validate(created)


@router.put("/{staff_id}", response_model=UserResponse)
def update_staff(
    staff_id: int,
    staff_in: UserUpdate,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    if current_admin.role == "super_admin":
        user = repo.get_by_id(staff_id)
    else:
        user = repo.get_by_id_and_store(staff_id, current_admin.store_id)

    if not user:
        raise HTTPException(status_code=404, detail="Staff member not found in your store")

    for key, val in staff_in.model_dump(exclude_unset=True).items():
        if key == "pin_code" and val is not None:
            user.pin_code = val
        elif key != "store_id":
            setattr(user, key, val)

    updated = repo.update(user)
    return UserResponse.model_validate(updated)


@router.delete("/{staff_id}")
def delete_staff(
    staff_id: int,
    current_admin: User = Depends(get_current_store_admin),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    if current_admin.role == "super_admin":
        user = repo.get_by_id(staff_id)
    else:
        user = repo.get_by_id_and_store(staff_id, current_admin.store_id)

    if not user:
        raise HTTPException(status_code=404, detail="Staff member not found in your store")

    user.is_active = False
    repo.update(user)
    return {"message": f"Staff member '{user.full_name}' deactivated"}
