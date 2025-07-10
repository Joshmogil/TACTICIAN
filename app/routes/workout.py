from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.auth import (

    get_current_user,

)

from app.db import workout as workout_db
from app.db.models import User
from app.workout import WorkoutWeek
from app.user import UserInfo

class WorkoutChunkCreate(BaseModel):
    """Payload for creating a workout chunk."""

    user_id: UUID
    workouts: WorkoutWeek


class WorkoutChunkUpdate(BaseModel):
    """Payload for updating a workout chunk."""

    workouts: WorkoutWeek


class WorkoutChunkOut(BaseModel):
    """Representation of a workout chunk returned by the API."""

    id: UUID
    user_id: UUID
    workouts: WorkoutWeek
    created_at: datetime
    completed_at: Optional[datetime] = None


router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutChunkOut)
async def create_workout_chunk(payload: WorkoutChunkCreate, current_user: User = Depends(get_current_user)) -> WorkoutChunkOut:
    """Create a new workout chunk for a user."""

    chunk = await workout_db.create_workout_chunk(
        payload.user_id, payload.workouts
    )
    return WorkoutChunkOut(
        id=chunk.id,
        user_id=chunk.user_id,
        workouts=payload.workouts,
        created_at=chunk.created_at,
        completed_at=chunk.completed_at,
    )


@router.get("/{chunk_id}", response_model=WorkoutChunkOut)
async def read_workout_chunk(chunk_id: UUID, current_user: User = Depends(get_current_user)) -> WorkoutChunkOut:
    """Retrieve a workout chunk by its ID."""

    chunk = await workout_db.get_workout_chunk(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Workout chunk not found")

    return WorkoutChunkOut(
        id=chunk.id,
        user_id=chunk.user_id,
        workouts=WorkoutWeek(**chunk.workouts),
        created_at=chunk.created_at,
        completed_at=chunk.completed_at,
    )


@router.put("/{chunk_id}", response_model=WorkoutChunkOut)
async def update_workout_chunk(
    chunk_id: UUID, payload: WorkoutChunkUpdate, current_user: User = Depends(get_current_user)
) -> WorkoutChunkOut:
    """Update the workouts for an existing chunk."""

    chunk = await workout_db.update_workout_chunk(chunk_id, payload.workouts)
    if not chunk:
        raise HTTPException(status_code=404, detail="Workout chunk not found")

    return WorkoutChunkOut(
        id=chunk.id,
        user_id=chunk.user_id,
        workouts=payload.workouts,
        created_at=chunk.created_at,
        completed_at=chunk.completed_at,
    )

