from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.auth import (
    get_current_user
)


from app.user import UserInfo
from app.db.models import User
import app.db.user as user_db


class UserCreate(BaseModel):
    """Payload for creating a new user."""

    email: EmailStr
    info: UserInfo


class UserUpdate(BaseModel):
    """Payload for updating an existing user."""

    info: UserInfo


class UserOut(UserCreate):
    """Representation of a user returned by the API."""

    id: UUID


router = APIRouter(prefix="/users", tags=["users"])


#@router.post("/", response_model=UserOut)
#async def create_user(payload: UserCreate) -> UserOut:
#    """Create a new user profile."""
#
#    user = await user_db.create_user(email=payload.email, info=payload.info)
#    return UserOut(id=user.id, email=user.email, info=payload.info)


@router.get("/", response_model=UserOut)
async def read_user(current_user: User = Depends(get_current_user)) -> UserOut:
    """Retrieve a user by email."""

    user = await user_db.get_user_by_email(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(id=user.id, email=user.email, info=User(**user.info))


@router.put("/", response_model=UserOut)
async def update_user(payload: UserUpdate, current_user: User = Depends(get_current_user)) -> UserOut:
    """Update the profile for an existing user."""

    updated = await user_db.update_user_profile(current_user.id, payload.info)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(id=updated.id, email=updated.email, info=payload.info)

