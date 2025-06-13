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


def recommend_workout(
    user: User,
    *,
    max_exercises: int = 5,
    fatigue_threshold: float = 100.0,
) -> Union[List[Dict[str, Union[str, float, int]]], str]:
    """Return recommended exercises with basic parameters or ``"rest"``.

    Each recommendation includes the exercise ``name`` and, when available,
    suggested ``reps``/``weight`` for weighted movements or ``duration`` and
    ``heart_rate`` for cardio.
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
            "weight_total": 0.0,
            "reps_total": 0.0,
            "duration_total": 0.0,
            "hr_total": 0.0,
        }
    )
    for record in user.workouts:
        if record.date < cutoff:
            continue
        for item in record.work_done:
            if isinstance(item, WeightedSet):
                stats = history[item.exercise_name]
                stats["workload"] += item.workload
                stats["count"] += 1
                weight = item.ac_weight if item.ac_weight else item.ex_weight
                reps = item.ac_reps if item.ac_reps else item.ex_reps
                stats["weight_total"] += weight
                stats["reps_total"] += reps
            elif isinstance(item, CardioSession):
                stats = history[item.exercise_name]
                stats["workload"] += item.workload
                stats["count"] += 1
                duration = (
                    item.ac_duration if item.ac_duration else item.ex_duration
                )
                hr = (
                    item.ac_heart_rate
                    if item.ac_heart_rate
                    else item.ex_heart_rate
                )
                stats["duration_total"] += duration
                stats["hr_total"] += hr

    # score candidate exercises
    scored: List[tuple[float, Dict[str, Union[str, float, int]]]] = []
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

        rec: Dict[str, Union[str, float, int]] = {"name": ex["name"]}
        if stats and stats["count"]:
            if movement == Movement.CARDIO:
                rec["duration"] = stats["duration_total"] / stats["count"]
                rec["heart_rate"] = stats["hr_total"] / stats["count"]
            else:
                rec["weight"] = stats["weight_total"] / stats["count"]
                rec["reps"] = int(round(stats["reps_total"] / stats["count"]))

        score = base * muscle_factor * quality_factor * intensity_factor
        scored.append((score, rec))

    scored.sort(key=lambda t: t[0], reverse=True)
    return [rec for _, rec in scored[:max_exercises]] if scored else "rest"
