from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from math import ceil
from typing import DefaultDict, Dict, List, Union

from app.models import User, ExperienceLevel
from core import (
    CardioSession,
    Exercise,
    Movement,
    Muscle,
    MuscleQuality,
    MuscleUsage,
    PercievedExertion,
    WeightedSet,
    WorkDone,
)
from load_exercises import load_exercises

# load exercise library once
EXERCISES: Dict[str, dict] = load_exercises()


DEFAULT_WEIGHT = 20.0
DEFAULT_REPS = 10
DEFAULT_DURATION = 20
DEFAULT_HR = 120
DEFAULT_SETS = 3

# Desired fatigue level after completing a session for each movement pattern
TARGET_FATIGUE: Dict[Movement, float] = {
    Movement.UPPER_PUSH: 100.0,
    Movement.UPPER_PULL: 100.0,
    Movement.LOWER_PUSH: 100.0,
    Movement.LOWER_PULL: 100.0,
    Movement.CORE: 80.0,
    Movement.FUNCTIONAL: 80.0,
    Movement.LOWER_PLYO: 80.0,
    Movement.UPPER_PLYO: 80.0,
    Movement.CARDIO: 80.0,
}


EXPERIENCE_FACTORS: Dict[ExperienceLevel, float] = {
    ExperienceLevel.BEGINNER: 0.75,
    ExperienceLevel.INTERMEDIATE: 1.0,
    ExperienceLevel.ADVANCED: 1.25,
}


def weekly_fatigue_targets(user: User) -> Dict[Movement, float]:
    """Return weekly fatigue targets scaled by experience level."""
    factor = EXPERIENCE_FACTORS.get(user.experience, 1.0)
    return {m: target * factor for m, target in TARGET_FATIGUE.items()}


DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def estimate_sessions_per_week(user: User, weeks: int = 4, default: int = 3) -> int:
    """Estimate training frequency from history or user setting."""
    if user.workouts_per_week:
        return user.workouts_per_week

    if not user.workouts:
        return default

    cutoff = datetime.utcnow() - timedelta(days=7 * weeks)
    weekly_counts: DefaultDict[int, int] = defaultdict(int)
    for w in user.workouts:
        if w.date < cutoff:
            continue
        week = w.date.isocalendar()[1]
        weekly_counts[week] += 1
    if not weekly_counts:
        return default
    return int(round(sum(weekly_counts.values()) / len(weekly_counts)))


def suggest_weekly_movements(
    user: User, workouts_per_week: int | None = None
) -> Dict[str, List[Movement]]:
    """Suggest movements for each day of the week."""
    sessions = workouts_per_week or estimate_sessions_per_week(user)
    sessions = max(1, min(7, sessions))
    allowed = user.allowed_movements or list(Movement)

    schedule: Dict[str, List[Movement]] = {day: [] for day in DAYS_OF_WEEK}
    idx = 0
    for movement in allowed:
        day = DAYS_OF_WEEK[idx % sessions]
        schedule[day].append(movement)
        idx += 1
    return schedule


def _build_plan(user: User, name: str, *, window: int = 3) -> Dict[str, object]:
    """Return a plan for the exercise using recent history.

    ``window`` defines how many past sessions to inspect when building the
    recommendation. The resulting plan includes an estimated number of sets for
    weighted movements based on those sessions.
    """

    weights: List[float] = []
    reps: List[int] = []
    workloads: List[float] = []
    set_counts: List[int] = []
    durations: List[float] = []
    heart_rates: List[int] = []

    # gather most recent sessions containing the exercise
    for rec in sorted(user.workouts, key=lambda r: r.date, reverse=True):
        session_items: List[WorkDone] = [
            item for item in rec.work_done if item.exercise_name == name
        ]
        if not session_items:
            continue
        set_counts.append(len(session_items))
        for item in session_items:
            if isinstance(item, WeightedSet):
                weight = item.ac_weight if item.ac_weight else item.ex_weight
                reps.append(item.ac_reps if item.ac_reps else item.ex_reps)
                weights.append(weight)
                workloads.append(item.workload)
            elif isinstance(item, CardioSession):
                duration = item.ac_duration if item.ac_duration else item.ex_duration
                hr = item.ac_heart_rate if item.ac_heart_rate else item.ex_heart_rate
                durations.append(duration)
                heart_rates.append(hr)
        if len(set_counts) >= window:
            break

    info = EXERCISES.get(name)
    movement = info.get("movement") if info else ""

    if movement == Movement.CARDIO.value:
        dur = sum(durations) / len(durations) if durations else DEFAULT_DURATION
        hr = sum(heart_rates) / len(heart_rates) if heart_rates else DEFAULT_HR
        avg_work = sum(workloads) / len(workloads) if workloads else dur
        return {
            "name": name,
            "duration": int(round(dur)),
            "heart_rate": int(round(hr)),
            "avg_work": avg_work,
        }

    wt = sum(weights) / len(weights) if weights else DEFAULT_WEIGHT
    rp = sum(reps) / len(reps) if reps else DEFAULT_REPS
    sets = int(round(sum(set_counts) / len(set_counts))) if set_counts else DEFAULT_SETS
    avg_work = sum(workloads) / len(workloads) if workloads else wt * rp
    return {
        "name": name,
        "weight": round(wt, 1),
        "reps": int(round(rp)),
        "sets": sets,
        "avg_work": avg_work,
    }


def recommend_workout(
    user: User,
    *,
    max_exercises: int = 5,
    fatigue_threshold: float = 100.0,
) -> Union[List[Dict[str, Union[str, float, int]]], str]:
    """Return a list of individual set recommendations or ``"rest"``.

    The function looks at the user's recovery scores and recent history to
    propose single sets (or cardio blocks) that gradually build fatigue toward
    the user's weekly fatigue targets. Sets are added only until the target for
    a movement is reached so recommendations don't overshoot the desired
    workload.
    """
    now = datetime.utcnow()
    user.recovery.decay(now)

    # determine which movement patterns are too fatigued
    fatigued = {
        m for m, score in user.recovery.scores.items() if score > fatigue_threshold
    }

    # gather allowed movements in order of least fatigue
    movements = sorted(
        [(m, user.recovery.scores.get(m, 0.0)) for m in Movement],
        key=lambda t: t[1],
    )
    allowed_movements = [
        m
        for m, score in movements
        if m not in fatigued and m in (user.allowed_movements or list(Movement))
    ]

    if not allowed_movements:
        return "rest"

    # build basic stats from recent workouts (last 7 days)
    cutoff = datetime.utcnow() - timedelta(days=7)
    history: DefaultDict[str, Dict[str, float]] = defaultdict(
        lambda: {
            "workload": 0.0,
            "count": 0,  # total sets logged
            "weight_total": 0.0,
            "reps_total": 0.0,
            "duration_total": 0.0,
            "hr_total": 0.0,
            "sessions": 0,  # number of sessions containing the exercise
        }
    )
    for record in user.workouts:
        if record.date < cutoff:
            continue
        session_counter: DefaultDict[str, int] = defaultdict(int)
        for item in record.work_done:
            if isinstance(item, WeightedSet):
                stats = history[item.exercise_name]
                stats["workload"] += item.workload
                stats["count"] += 1
                weight = item.ac_weight if item.ac_weight else item.ex_weight
                reps = item.ac_reps if item.ac_reps else item.ex_reps
                stats["weight_total"] += weight
                stats["reps_total"] += reps
                session_counter[item.exercise_name] += 1
            elif isinstance(item, CardioSession):
                stats = history[item.exercise_name]
                stats["workload"] += item.workload
                stats["count"] += 1
                duration = item.ac_duration if item.ac_duration else item.ex_duration
                hr = item.ac_heart_rate if item.ac_heart_rate else item.ex_heart_rate
                stats["duration_total"] += duration
                stats["hr_total"] += hr
                session_counter[item.exercise_name] += 1
        for ex_name, _sets in session_counter.items():
            history[ex_name]["sessions"] += 1

    # Build candidate plans and scores
    scored: List[Dict[str, Union[str, float, int]]] = []
    for ex in EXERCISES.values():
        movement = Movement(ex["movement"])
        if movement not in allowed_movements:
            continue

        muscles: List[MuscleUsage] = []
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
            ex_obj = Exercise(name=ex["name"], movement=movement, muscles=muscles)
        except Exception:
            continue

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
            avg_work_hist = stats["workload"] / stats["count"]
            intensity_factor = 1.0 / (1.0 + (avg_work_hist / 100.0))
        else:
            intensity_factor = 1.0

        plan = _build_plan(user, ex["name"])
        avg_work = plan.get("avg_work", 0.0)
        if stats and stats["count"]:
            if movement == Movement.CARDIO:
                plan["duration"] = int(round(stats["duration_total"] / stats["count"]))
                plan["heart_rate"] = int(round(stats["hr_total"] / stats["count"]))
            else:
                plan["weight"] = round(stats["weight_total"] / stats["count"], 1)
                plan["reps"] = int(round(stats["reps_total"] / stats["count"]))
                if stats["sessions"]:
                    plan["sets"] = int(round(stats["count"] / stats["sessions"]))
                    avg_work = stats["workload"] / stats["count"]

        plan["movement"] = movement
        plan["avg_work"] = avg_work
        score = base * muscle_factor * quality_factor * intensity_factor
        plan["score"] = score
        scored.append(plan)

    scored.sort(key=lambda p: p["score"], reverse=True)

    allocated: DefaultDict[Movement, float] = defaultdict(float)
    recommendations: List[Dict[str, Union[str, float, int]]] = []

    targets = weekly_fatigue_targets(user)

    for plan in scored:
        if len(recommendations) >= max_exercises:
            break

        movement: Movement = plan["movement"]  # type: ignore[assignment]
        target = targets.get(movement, fatigue_threshold)
        current = user.recovery.scores.get(movement, 0.0) + allocated[movement]
        needed = target - current
        if needed <= 0 or not plan["avg_work"]:
            continue

        rec_work = plan["avg_work"]  # type: ignore[index]
        sets_needed = int(ceil(needed / rec_work)) if rec_work else 1
        sets = min(sets_needed, max_exercises - len(recommendations))
        for _ in range(int(sets)):
            if len(recommendations) >= max_exercises or needed <= 0:
                break
            rec: Dict[str, Union[str, float, int]] = {"name": plan["name"]}
            if movement == Movement.CARDIO:
                rec["duration"] = plan["duration"]
                rec["heart_rate"] = plan["heart_rate"]
            else:
                rec["weight"] = plan["weight"]
                rec["reps"] = plan["reps"]

            rec["reason"] = (
                f"{movement.value.replace('_', ' ')} fatigue {current:.1f}/{target:.0f}. "
                f"This set adds about {rec_work:.1f} workload."
            )
            recommendations.append(rec)
            allocated[movement] += rec_work
            current += rec_work
            needed = target - current
            if needed <= 0:
                break

    return recommendations if recommendations else "rest"


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
