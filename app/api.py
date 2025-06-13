from __future__ import annotations

from datetime import datetime
from typing import Dict

from fastapi import APIRouter

from app.models import User
from app.recovery import update_recovery
from app.recommendation import recommend_workout
from workout import Workout

router = APIRouter()

# in-memory user storage
USERS: Dict[str, User] = {}


def get_user(user_id: str) -> User:
    if user_id not in USERS:
        USERS[user_id] = User(id=user_id, name=user_id)
    return USERS[user_id]


@router.post("/users/{user_id}/workouts")
def log_workout(user_id: str, workout: Workout):
    user = get_user(user_id)
    timestamp = datetime.combine(workout.date, datetime.min.time())
    update_recovery(user, workout.work_done, timestamp=timestamp)
    return {"status": "logged", "recovery": user.recovery.scores}


@router.get("/users/{user_id}/recovery")
def recovery_status(user_id: str):
    user = get_user(user_id)
    user.recovery.decay(datetime.utcnow())
    return user.recovery.scores


@router.get("/users/{user_id}/recommendations")
def workout_recommendations(user_id: str):
    """Return exercise recommendations with intensity suggestions."""
    user = get_user(user_id)
    recs = recommend_workout(user)
    return {"recommendations": recs}


@router.get("/users/{user_id}/snapshot")
def recovery_snapshot(user_id: str):
    """Return recovery scores and suggested movement patterns."""
    user = get_user(user_id)
    movements = [m.value for m in recommend_movements(user)]
    return {"recovery": user.recovery.scores, "recommended_movements": movements}
