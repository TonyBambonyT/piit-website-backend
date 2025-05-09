from sqlalchemy.orm import Session
from app.dao.models import AdminUser


class AdminUserDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> AdminUser | None:
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()

    def create(self, user: AdminUser):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
