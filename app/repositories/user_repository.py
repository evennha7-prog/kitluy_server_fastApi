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

    def get_by_phone(self, phone: str) -> Optional[User]:
        clean = phone.replace(" ", "").replace("-", "")
        return self.db.query(User).filter(
            or_(
                User.phone_number == phone,
                User.phone_number == clean,
                func.replace(func.replace(User.phone_number, " ", ""), "-", "") == clean,
            )
        ).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        clean_id = identifier.replace(" ", "").replace("-", "").strip()
        lower_id = identifier.lower().strip()
        clean_lower = clean_id.lower()

        return self.db.query(User).filter(
            or_(
                User.phone_number == identifier.strip(),
                User.phone_number == clean_id,
                func.replace(func.replace(User.phone_number, " ", ""), "-", "") == clean_id,
                func.lower(User.email) == lower_id,
                func.lower(User.full_name) == lower_id,
                func.lower(func.replace(User.full_name, " ", "")) == clean_lower,
                func.lower(User.telegram_username) == lower_id,
                func.lower(User.telegram_username) == f"@{lower_id}",
            )
        ).first()



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
