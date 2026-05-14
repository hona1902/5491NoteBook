from datetime import datetime
from typing import ClassVar, Optional

from loguru import logger

from open_notebook.database.repository import repo_query
from open_notebook.domain.base import ObjectModel


class UserPreferences(ObjectModel):
    table_name: ClassVar[str] = "user_preferences"
    nullable_fields: ClassVar[set[str]] = set()

    user_id: str
    theme: str = "system"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    async def get_for_user(cls, user_id: str) -> Optional["UserPreferences"]:
        """Returns the preferences record for the given user, or None."""
        result = await repo_query(
            "SELECT * FROM user_preferences WHERE user_id = $user_id LIMIT 1",
            {"user_id": user_id},
        )
        if result:
            return cls(**result[0])
        return None

    @classmethod
    async def get_or_default(cls, user_id: str) -> "UserPreferences":
        """Returns the preferences record for the given user, or a default
        UserPreferences instance (theme='system') without saving."""
        existing = await cls.get_for_user(user_id)
        if existing:
            return existing
        return cls(user_id=user_id, theme="system")
