from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.store import Store
from app.repositories.user_repository import UserRepository
from app.repositories.store_repository import StoreRepository
from app.services.store_service import StoreService
from app.schemas.auth import LoginRequest, PinLoginRequest, Token, ChangePasswordRequest, StoreRegisterRequest
from app.schemas.user import UserCreate, UserProfileUpdate, UserResponse, StaffCreate
from app.schemas.store import StoreCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.store_repo = StoreRepository(db)

    def _build_token_response(self, user: User) -> Token:
        store_name = user.store.store_name if user.store else None
        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            store_id=user.store_id,
        )
        user_resp = UserResponse.model_validate(user)
        user_resp.store_name = store_name
        return Token(
            access_token=access_token,
            role=user.role,
            store_id=user.store_id,
            store_name=store_name,
            user=user_resp,
        )

    def register_store(self, req: StoreRegisterRequest) -> Token:
        # Check phone / email conflict
        clean_phone = req.phone_number.replace(" ", "").replace("-", "")
        if self.user_repo.get_by_phone(req.phone_number) or self.user_repo.get_by_phone(clean_phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is already registered",
            )
        if req.email and self.user_repo.get_by_email(req.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        # 1. Create the store
        store_service = StoreService(self.db)
        store_create = StoreCreate(
            store_name=req.store_name,
            store_branch=req.store_branch or "Main Branch",
            store_code=req.store_code,
            address=req.address,
            currency_symbol=req.currency_symbol or "$",
            exchange_rate_khr=req.exchange_rate_khr or 4100.0,
        )
        store_resp = store_service.create_store(store_create)

        # 2. Create the Store Admin User
        hashed_password = get_password_hash(req.password)
        db_user = User(
            store_id=store_resp.id,
            full_name=req.admin_name,
            phone_number=req.phone_number,
            email=req.email,
            hashed_password=hashed_password,
            pin_code=req.pin_code,
            role="store_admin",
            shift="Store Manager (Full-Time)",
            avatar_index=0,
            is_active=True,
        )
        created_user = self.user_repo.create(db_user)

        # 3. Create StoreOwner profile in store_owners table
        from app.models.store_owner import StoreOwner
        store_owner = StoreOwner(
            user_id=created_user.id,
            store_id=store_resp.id,
            status="approved",
            business_type="Cafe & Beverage",
        )
        self.db.add(store_owner)
        self.db.commit()

        return self._build_token_response(created_user)

    def register(self, user_in: UserCreate) -> Token:
        clean_phone = user_in.phone_number.replace(" ", "").replace("-", "")
        if self.user_repo.get_by_phone(user_in.phone_number) or self.user_repo.get_by_phone(clean_phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is already registered",
            )
        if user_in.email and self.user_repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        # Default store_id fallback to 1 if not specified
        target_store_id = user_in.store_id or 1

        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            store_id=target_store_id,
            full_name=user_in.full_name,
            phone_number=user_in.phone_number,
            email=user_in.email,
            hashed_password=hashed_password,
            pin_code=user_in.pin_code,
            role=user_in.role or "cashier",
            shift=user_in.shift or "Morning Shift (06:30 AM - 03:00 PM)",
            avatar_index=user_in.avatar_index or 0,
            is_active=True,
        )
        created_user = self.user_repo.create(db_user)
        return self._build_token_response(created_user)

    def login(self, login_data: LoginRequest) -> Token:
        user = self.user_repo.get_by_identifier(login_data.identifier)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number/email or password",
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Account is disabled")

        return self._build_token_response(user)

    def login_with_pin(self, pin_data: PinLoginRequest) -> Token:
        user = self.user_repo.get_by_pin(pin_data.pin, store_id=pin_data.store_id)
        if not user:
            # Fallback for general demo PIN lookup
            user = self.user_repo.get_by_pin(pin_data.pin)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid cashier PIN",
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Account is disabled")

        return self._build_token_response(user)

    def update_profile(self, user: User, profile_in: UserProfileUpdate) -> UserResponse:
        if profile_in.full_name is not None:
            user.full_name = profile_in.full_name
        if profile_in.phone_number is not None:
            user.phone_number = profile_in.phone_number
        if profile_in.email is not None:
            user.email = profile_in.email
        if profile_in.role is not None and user.role == "super_admin":
            user.role = profile_in.role
        if profile_in.shift is not None:
            user.shift = profile_in.shift
        if profile_in.avatar_index is not None:
            user.avatar_index = profile_in.avatar_index

        updated_user = self.user_repo.update(user)
        resp = UserResponse.model_validate(updated_user)
        resp.store_name = user.store.store_name if user.store else None
        return resp

    def change_password(self, user: User, req: ChangePasswordRequest) -> dict:
        if req.new_password:
            if req.current_password and not verify_password(req.current_password, user.hashed_password):
                raise HTTPException(status_code=400, detail="Current password incorrect")
            user.hashed_password = get_password_hash(req.new_password)

        if req.new_pin:
            user.pin_code = req.new_pin

        self.user_repo.update(user)
        return {"message": "Credentials updated successfully"}
