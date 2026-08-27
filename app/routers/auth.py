from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, PinLoginRequest, Token, ChangePasswordRequest, StoreRegisterRequest
from app.schemas.user import UserCreate, UserProfileUpdate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-store", response_model=Token)
def register_store(req: StoreRegisterRequest, db: Session = Depends(get_db)):
    """
    SaaS Registration: Create a new Store and its Store Admin account.
    """
    auth_service = AuthService(db)
    return auth_service.register_store(req)


@router.get("/registration-status")
def get_registration_status(phone: str, db: Session = Depends(get_db)):
    """
    Public endpoint for Store Owners to check their registration approval status by phone number.
    """
    auth_service = AuthService(db)
    return auth_service.check_registration_status(phone)


@router.post("/register", response_model=Token)

def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a user account under a specified store_id.
    """
    auth_service = AuthService(db)
    return auth_service.register(user_in)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with phone number or email and password.
    Returns JWT access token with role and store tenancy.
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.post("/pin-login", response_model=Token)
def pin_login(pin_data: PinLoginRequest, db: Session = Depends(get_db)):
    """
    Quick POS 4-digit PIN login for store cashiers.
    """
    auth_service = AuthService(db)
    return auth_service.login_with_pin(pin_data)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    user_resp = UserResponse.model_validate(current_user)
    user_resp.store_name = current_user.store.store_name if current_user.store else None
    return user_resp


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    return auth_service.update_profile(current_user, profile_in)


@router.put("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    return auth_service.change_password(current_user, req)
