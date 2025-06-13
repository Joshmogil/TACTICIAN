from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Union

from core import Movement
from app.models import User
from load_exercises import load_exercises

# load exercise library once
EXERCISES: Dict[str, dict] = load_exercises()


def recommend_workout(
    user: User,
    *,
    max_exercises: int = 5,
    fatigue_threshold: float = 100.0,
) -> Union[List[str], str]:
    """Return a list of recommended exercise names or 'rest'."""
    # ensure recovery decay applied to current time
    user.recovery.decay(datetime.utcnow())

    # determine which movement patterns are too fatigued
    fatigued = {
        m
        for m, score in user.recovery.scores.items()
        if score > fatigue_threshold
    }

    # gather allowed movements in order of least fatigue
    movements = sorted(
        [(m, user.recovery.scores.get(m, 0.0)) for m in Movement],
        key=lambda t: t[1],
    )
    allowed_movements = [m for m, score in movements if m not in fatigued]

    if not allowed_movements:
        return "rest"

    # collect exercises from permitted movements
    candidates = [
        ex["name"]
        for ex in EXERCISES.values()
        if Movement(ex["movement"]) in allowed_movements
    ]
    return candidates[:max_exercises]
