from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.recovery import WorkoutRecord

from collections import defaultdict

from core import (
    CardioSession,
    Exercise,
    Movement,
    Muscle,
    MuscleQuality,
    MuscleUsage,
    WeightedSet,
    WorkDone,
    DEFAULT_BODYWEIGHT,
    aggregate_muscle_workload,
    aggregate_workload,
)
from load_exercises import load_exercises


class RecoveryState(BaseModel):
    """Stores fatigue levels for each movement pattern."""

    scores: Dict[Movement, float] = {}
    muscle_scores: Dict[Muscle, float] = {}
    quality_scores: Dict[MuscleQuality, float] = {}
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
        for mus in list(self.muscle_scores):
            self.muscle_scores[mus] *= factor
        for q in list(self.quality_scores):
            self.quality_scores[q] *= factor
        self.last_update = now

    def apply_workout(self, work: List[WorkDone], now: datetime) -> None:
        """Update recovery state given new work completed."""
        self.decay(now)
        totals = aggregate_workload(work)
        for m, amount in totals.items():
            self.scores[m] = self.scores.get(m, 0.0) + amount

        raw_ex = load_exercises()
        exercises: Dict[str, Exercise] = {}
        for n, d in raw_ex.items():
            muscles = []
            for md in d.get("muscles", []):
                try:
                    muscles.append(
                        MuscleUsage(
                            muscle=Muscle(md["muscle"]),
                            amount=float(md["amount"]),
                            quality=MuscleQuality(md["quality"]),
                        )
                    )
                except Exception:
                    continue
            try:
                exercises[n] = Exercise(
                    name=n, movement=Movement(d["movement"]), muscles=muscles
                )
            except Exception:
                continue

        muscle_totals = aggregate_muscle_workload(work, exercises)
        for mus, amt in muscle_totals.items():
            self.muscle_scores[mus] = self.muscle_scores.get(mus, 0.0) + amt

        quality_totals: Dict[MuscleQuality, float] = defaultdict(float)
        for item in work:
            if isinstance(item, (WeightedSet, CardioSession)):
                ex = exercises.get(item.exercise_name)
                if not ex:
                    continue
                for usage in ex.muscles:
                    quality_totals[usage.quality] += item.workload * usage.amount

        for q, amt in quality_totals.items():
            self.quality_scores[q] = self.quality_scores.get(q, 0.0) + amt


class User(BaseModel):
    id: str
    name: str
    default_bodyweight: float = DEFAULT_BODYWEIGHT
    recovery: RecoveryState = RecoveryState()
    workouts: List["WorkoutRecord"] = []
