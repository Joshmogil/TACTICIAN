from uuid import UUID
from typing import Optional

from tortoise.exceptions import DoesNotExist

from app.db import models
from app.user import UserInfo


async def create_user(email: str, info: UserInfo) -> models.User:
    """Create a new user in the database."""
    user = await models.User.create(email=email, info=info.model_dump())
    return user


async def get_user_by_email(email: str) -> Optional[models.User]:
    """Retrieve a user by email address."""
    try:
        return await models.User.get(email=email)
    except DoesNotExist:
        return None


async def update_user_profile(user_id: UUID, info: UserInfo) -> Optional[models.User]:
    """Update the JSON profile for a user."""
    try:
        user = await models.User.get(id=user_id)
    except DoesNotExist:
        return None

    user.info = info.model_dump()
    await user.save()
    return user
