from typing import Optional
from sqlalchemy.orm import Session
from app.models.setting import StoreSetting


class SettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self, store_id: int) -> Optional[StoreSetting]:
        return self.db.query(StoreSetting).filter(StoreSetting.store_id == store_id).first()

    def create(self, setting: StoreSetting) -> StoreSetting:
        self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def update(self, setting: StoreSetting) -> StoreSetting:
        self.db.commit()
        self.db.refresh(setting)
        return setting
