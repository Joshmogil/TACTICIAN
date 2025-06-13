from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from typing import TYPE_CHECKING
from pydantic import BaseModel


if TYPE_CHECKING:
    from app.recovery import WorkoutRecord
from core import Movement, WorkDone, aggregate_workload


class RecoveryState(BaseModel):
    """Stores fatigue levels for each movement pattern."""

    scores: Dict[Movement, float] = {}
    last_update: Optional[datetime] = None

    def decay(self, now: datetime, half_life_hours: float = 48) -> None:
        """Apply exponential decay to all scores based on time since last update."""
        if self.last_update is None:
            self.last_update = now
            return
        hours = (now - self.last_update).total_seconds() / 3600
        factor = 0.5 ** (hours / half_life_hours)
        for m in list(self.scores):
            self.scores[m] *= factor
        self.last_update = now

    def apply_workout(self, work: List[WorkDone], now: datetime) -> None:
        """Update recovery state given new work completed."""
        self.decay(now)
        totals = aggregate_workload(work)
        for m, amount in totals.items():
            self.scores[m] = self.scores.get(m, 0.0) + amount


class User(BaseModel):
    id: str
    name: str
    recovery: RecoveryState = RecoveryState()
    workouts: List['WorkoutRecord'] = []




