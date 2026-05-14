from datetime import datetime
from typing import ClassVar, Optional

from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel

from open_notebook.database.repository import repo_query
from open_notebook.domain.base import ObjectModel

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AppUser(ObjectModel):
    table_name: ClassVar[str] = "app_user"
    nullable_fields: ClassVar[set[str]] = {"last_login_at", "password_hash"}

    username: str
    email: str
    password_hash: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    def verify_password(self, plain_password: str) -> bool:
        if not self.password_hash:
            return False
        return pwd_context.verify(plain_password, self.password_hash)

    def set_password(self, new_password: str) -> None:
        self.password_hash = pwd_context.hash(new_password)

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["AppUser"]:
        result = await repo_query(
            "SELECT * FROM app_user WHERE username = $username",
            {"username": username},
        )
        if result:
            return cls(**result[0])
        return None

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["AppUser"]:
        result = await repo_query(
            "SELECT * FROM app_user WHERE email = $email",
            {"email": email},
        )
        if result:
            return cls(**result[0])
        return None

    @classmethod
    async def create_user(
        cls, username: str, email: str, password: str, role: str = "user"
    ) -> "AppUser":
        user = cls(username=username, email=email, role=role)
        user.set_password(password)
        await user.save()
        return user


class AppUserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    @classmethod
    def from_user(cls, user: AppUser) -> "AppUserResponse":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )
