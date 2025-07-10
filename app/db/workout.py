from uuid import UUID
from typing import Optional

from tortoise.exceptions import DoesNotExist

from app.db import models
from app.workout import WorkoutWeek


async def create_workout_chunk(
    user_id: UUID, workouts: WorkoutWeek
) -> models.WorkoutChunk:
    """Create a new workout chunk for a user."""
    chunk = await models.WorkoutChunk.create(
        user_id=user_id, workouts=workouts.model_dump()
    )
    return chunk


async def get_workout_chunk(chunk_id: UUID) -> Optional[models.WorkoutChunk]:
    """Retrieve a workout chunk by its ID."""
    try:
        return await models.WorkoutChunk.get(id=chunk_id)
    except DoesNotExist:
        return None


async def update_workout_chunk(
    chunk_id: UUID, workouts: WorkoutWeek
) -> Optional[models.WorkoutChunk]:
    """Update the workouts JSON for a chunk."""
    chunk = await get_workout_chunk(chunk_id)
    if not chunk:
        return None

    chunk.workouts = workouts.model_dump()
    await chunk.save()
    return chunk
