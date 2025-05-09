from passlib.hash import bcrypt

from app.api.dto import AdminRegisterRequest
from app.dao.entities.auth_dao import AdminUserDAO
from app.dao.models import AdminUser


class AdminUserService:
    def __init__(self, db):
        self.dao = AdminUserDAO(db)

    def register_admin(self, request: AdminRegisterRequest):
        existing = self.dao.get_by_username(request.username)
        if existing:
            raise ValueError("User already exists")

        hashed_password = bcrypt.hash(request.password)
        admin = AdminUser(username=request.username, password_hash=hashed_password)
        return self.dao.create(admin)

    def validate_credentials(self, username: str, password: str) -> AdminUser | None:
        user = self.dao.get_by_username(username)
        if user and bcrypt.verify(password, user.password_hash):
            return user
        return None
