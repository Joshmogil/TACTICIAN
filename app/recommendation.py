from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, Dict, List, Union

from app.models import User
from core import (
    CardioSession,
    Exercise,
    Movement,
    Muscle,
    MuscleQuality,
    MuscleUsage,
    PercievedExertion,
    WeightedSet,
)
from load_exercises import load_exercises

# load exercise library once
EXERCISES: Dict[str, dict] = load_exercises()


DEFAULT_WEIGHT = 20.0
DEFAULT_REPS = 10
DEFAULT_DURATION = 20
DEFAULT_HR = 120


def _build_plan(user: User, name: str) -> Dict[str, object]:
    """Return a simple plan for the exercise based on history."""
    weights: List[float] = []
    reps: List[int] = []
    durations: List[float] = []
    heart_rates: List[int] = []

    for rec in user.workouts:
        for item in rec.work_done:
            if item.exercise_name != name:
                continue
            if isinstance(item, WeightedSet):
                if item.ac_weight or item.ex_weight:
                    weights.append(item.ac_weight or item.ex_weight)
                if item.ac_reps or item.ex_reps:
                    reps.append(item.ac_reps or item.ex_reps)
            elif isinstance(item, CardioSession):
                if item.ac_duration or item.ex_duration:
                    durations.append(item.ac_duration or item.ex_duration)
                if item.ac_heart_rate or item.ex_heart_rate:
                    heart_rates.append(item.ac_heart_rate or item.ex_heart_rate)

    info = EXERCISES.get(name)
    movement = info.get("movement") if info else ""

    if movement == Movement.CARDIO.value:
        dur = sum(durations) / len(durations) if durations else DEFAULT_DURATION
        hr = sum(heart_rates) / len(heart_rates) if heart_rates else DEFAULT_HR
        return {"name": name, "duration": int(round(dur)), "heart_rate": int(round(hr))}

    wt = sum(weights) / len(weights) if weights else DEFAULT_WEIGHT
    rp = sum(reps) / len(reps) if reps else DEFAULT_REPS
    return {"name": name, "weight": round(wt, 1), "reps": int(round(rp))}


def recommend_workout(
    user: User,
    *,
    max_exercises: int = 5,
    fatigue_threshold: float = 100.0,
 ) -> Union[List[Dict[str, object]], str]:
    """Return a list of workout plans or ``"rest"``.

    The algorithm combines the user's recovery state with recent workout
    history. Exercises performed frequently and at high intensity in the recent
    past receive a lower score so the recommendations naturally rotate through
    movements and account for perceived effort.
    """
    # ensure recovery decay applied to current time
    user.recovery.decay(datetime.utcnow())

    # determine which movement patterns are too fatigued
    fatigued = {
        m for m, score in user.recovery.scores.items() if score > fatigue_threshold
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
    history: DefaultDict[str, Dict[str, float]] = defaultdict(
        lambda: {
            "workload": 0.0,
            "count": 0,
        }
    )
    for record in user.workouts:
        if record.date < cutoff:
            continue
        for item in record.work_done:
            if isinstance(item, (WeightedSet, CardioSession)):
                stats = history[item.exercise_name]
                stats["workload"] += item.workload
                stats["count"] += 1

    # score candidate exercises
    scored: List[tuple[float, str]] = []
    for ex in EXERCISES.values():
        movement = Movement(ex["movement"])
        if movement not in allowed_movements:
            continue

        muscles = []
        for md in ex.get("muscles", []):
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
            ex_obj = Exercise(
                name=ex["name"], movement=Movement(ex["movement"]), muscles=muscles
            )
        except Exception:
            continue

        # base factors from recovery
        base = 1.0 / (1.0 + user.recovery.scores.get(movement, 0.0) / 100.0)

        muscle_fatigues = [
            user.recovery.muscle_scores.get(u.muscle, 0.0) for u in ex_obj.muscles
        ]
        quality_fatigues = [
            user.recovery.quality_scores.get(u.quality, 0.0) for u in ex_obj.muscles
        ]

        muscle_factor = 1.0 / (
            1.0 + (max(muscle_fatigues) if muscle_fatigues else 0.0) / 100.0
        )
        quality_factor = 1.0 / (
            1.0 + (max(quality_fatigues) if quality_fatigues else 0.0) / 100.0
        )

        stats = history.get(ex["name"])
        if stats and stats["count"]:
            avg_work = stats["workload"] / stats["count"]
            intensity_factor = 1.0 / (1.0 + (avg_work / 100.0))
        else:
            intensity_factor = 1.0

        score = base * muscle_factor * quality_factor * intensity_factor
        scored.append((score, ex["name"]))

    scored.sort(key=lambda t: t[0], reverse=True)
    if not scored:
        return "rest"

    plans: List[Dict[str, object]] = []
    for _, name in scored[:max_exercises]:
        plans.append(_build_plan(user, name))

    return plans


def recommend_movements(
    user: User, *, fatigue_threshold: float = 100.0
) -> List[Movement]:
    """Return movement patterns suitable for the next session.

    The movements are sorted from least to most fatigued and filtered using the
    provided ``fatigue_threshold``.
    """
    user.recovery.decay(datetime.utcnow())
    scored = sorted(
        [(m, user.recovery.scores.get(m, 0.0)) for m in Movement],
        key=lambda t: t[1],
    )
    return [m for m, score in scored if score <= fatigue_threshold]
