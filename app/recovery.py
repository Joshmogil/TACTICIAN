from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
from typing import List

from core import WorkDone
from app.models import User


def update_recovery(user: User, work: List[WorkDone], *, timestamp: datetime | None = None) -> None:
    """Update a user's recovery state with the completed work."""
    now = timestamp or datetime.utcnow()
    user.recovery.apply_workout(work, now)
    user.workouts.append(
        WorkoutRecord(date=now, work_done=work)
    )


class WorkoutRecord(BaseModel):
    date: datetime
    work_done: List[WorkDone]


# resolve forward reference in User once WorkoutRecord is defined
try:
    User.model_rebuild()
except AttributeError:
    User.update_forward_refs(WorkoutRecord=WorkoutRecord)

