from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any, List
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Query, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str = "cashier",
    store_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "store_id": store_id,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
):
    from app.models.user import User

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")
    return user


def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
):
    from app.models.user import User

    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        return None
    return None


def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return current_user


def require_roles(*allowed_roles: str):
    """
    Dependency factory to check if the current user has one of the allowed roles.
    e.g. Depends(require_roles("super_admin", "store_admin"))
    """
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: user role '{current_user.role}' does not have permission",
            )
        return current_user
    return role_checker


def get_current_store_admin(current_user = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "store_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Requires Store Admin privileges",
        )
    return current_user


def get_current_super_admin(current_user = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "admin", "store_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Requires Administrator privileges",
        )
    return current_user


def get_tenant_store_id(
    store_id: Optional[int] = Query(None, description="Optional store_id filter (Super Admin only)"),
    x_store_id: Optional[int] = Header(None, alias="X-Store-Id", description="Store ID passed in header"),
    current_user = Depends(get_optional_current_user),
) -> int:
    """
    Resolves the store_id for multi-tenant requests.
    - If user is logged in and is not super_admin: strictly returns their current_user.store_id.
    - If user is super_admin: returns query store_id or X-Store-Id header or fallback to 1.
    - If unauthenticated: returns query store_id or X-Store-Id header or fallback to 1.
    """
    if current_user:
        if current_user.role != "super_admin" and current_user.store_id:
            return current_user.store_id
        if current_user.role == "super_admin":
            return store_id or x_store_id or current_user.store_id or 1
    return store_id or x_store_id or 1

