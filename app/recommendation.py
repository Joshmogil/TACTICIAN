from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Union, DefaultDict

from collections import defaultdict

from core import Movement, WeightedSet, PercievedExertion
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
    """Return a list of recommended exercise names or ``"rest"``.

    The algorithm combines the user's recovery state with recent workout
    history. Exercises performed frequently and at high intensity in the recent
    past receive a lower score so the recommendations naturally rotate through
    movements and account for perceived effort.
    """
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

    # build basic stats from recent workouts (last 7 days)
    cutoff = datetime.utcnow() - timedelta(days=7)
    history: DefaultDict[str, Dict[str, float]] = defaultdict(lambda: {
        "sets": 0,
        "reps": 0,
        "intensity": 0.0,
        "count": 0,
    })
    for record in user.workouts:
        if record.date < cutoff:
            continue
        for item in record.work_done:
            if isinstance(item, WeightedSet):
                stats = history[item.exercise_name]
                stats["sets"] += 1
                reps = item.ac_reps if item.ac_reps else item.ex_reps
                stats["reps"] += reps
                intensity = int(item.pe.value) / int(PercievedExertion.MAX.value)
                stats["intensity"] += intensity
                stats["count"] += 1

    # score candidate exercises
    scored: List[tuple[float, str]] = []
    for ex in EXERCISES.values():
        movement = Movement(ex["movement"])
        if movement not in allowed_movements:
            continue

        base = 1.0 / (1.0 + user.recovery.scores.get(movement, 0.0))
        stats = history.get(ex["name"])
        if stats and stats["count"]:
            avg_int = stats["intensity"] / stats["count"]
            avg_reps = stats["reps"] / stats["count"]
            intensity_factor = 1.0 / (1.0 + avg_int * avg_reps)
        else:
            intensity_factor = 1.0
        score = base * intensity_factor
        scored.append((score, ex["name"]))

    scored.sort(key=lambda t: t[0], reverse=True)
    return [name for _, name in scored[:max_exercises]] if scored else "rest"
