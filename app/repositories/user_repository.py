from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_id_and_store(self, user_id: int, store_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id, User.store_id == store_id).first()

    def _generate_phone_variants(self, phone: str) -> List[str]:
        raw = phone.strip()
        clean = raw.replace(" ", "").replace("-", "").replace(".", "")
        variants = {raw, clean}
        if len(clean) == 10:
            variants.add(f"{clean[:3]} {clean[3:5]} {clean[5:7]} {clean[7:]}")
            variants.add(f"{clean[:3]} {clean[3:6]} {clean[6:]}")
        elif len(clean) == 9:
            variants.add(f"{clean[:3]} {clean[3:5]} {clean[5:7]} {clean[7:]}")
            variants.add(f"{clean[:3]} {clean[3:6]} {clean[6:]}")
        return list(variants)

    def get_by_phone(self, phone: str) -> Optional[User]:
        variants = self._generate_phone_variants(phone)
        user = self.db.query(User).filter(User.phone_number.in_(variants)).first()
        if user:
            return user
        clean = phone.replace(" ", "").replace("-", "").strip()
        return self.db.query(User).filter(
            func.replace(func.replace(User.phone_number, " ", ""), "-", "") == clean
        ).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.strip().lower()).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        ident = identifier.strip()
        lower_id = ident.lower()
        variants = self._generate_phone_variants(ident)

        # 1. Fast indexed lookups: phone variants, email, username
        user = (
            self.db.query(User)
            .filter(
                or_(
                    User.phone_number.in_(variants),
                    User.email == lower_id,
                    User.telegram_username == ident,
                    User.telegram_username == f"@{ident.lstrip('@')}",
                    User.full_name == ident,
                )
            )
            .first()
        )
        if user:
            return user

        # 2. Fallback case-insensitive / space-stripped lookup
        clean_id = ident.replace(" ", "").replace("-", "")
        clean_lower = clean_id.lower()
        return (
            self.db.query(User)
            .filter(
                or_(
                    func.replace(func.replace(User.phone_number, " ", ""), "-", "") == clean_id,
                    func.lower(User.email) == lower_id,
                    func.lower(User.full_name) == lower_id,
                    func.lower(func.replace(User.full_name, " ", "")) == clean_lower,
                    func.lower(User.telegram_username) == lower_id,
                )
            )
            .first()
        )




    def get_by_pin(self, pin: str, store_id: Optional[int] = None) -> Optional[User]:
        query = self.db.query(User).filter(User.pin_code == pin, User.is_active == True)
        if store_id is not None:
            query = query.filter(User.store_id == store_id)
        return query.first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def list_by_store(self, store_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).filter(User.store_id == store_id).offset(skip).limit(limit).all()

    def count_by_store(self, store_id: int) -> int:
        return self.db.query(User).filter(User.store_id == store_id).count()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
