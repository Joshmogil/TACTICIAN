import datetime as dt

from app.models import User
from app.recommendation import (
    recommend_workout,
    recommend_movements,
    weekly_fatigue_targets,
    suggest_weekly_movements,
)
from app.recovery import update_recovery
from core import CardioSession, Movement, PercievedExertion, WeightedSet


def test_recommendation_returns_individual_sets():
    user = User(id="u1", name="User")
    ws = WeightedSet(
        exercise_name="Dumbbell Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=20,
        ac_weight=20,
        ex_reps=5,
        ac_reps=5,
        pe=PercievedExertion.HIGH,
    )
    update_recovery(user, [ws], timestamp=dt.datetime.utcnow())
    recs = recommend_workout(user, max_exercises=5)
    assert isinstance(recs, list) and recs
    for item in recs:
        assert "name" in item
        assert "reason" in item
        if "reps" in item:
            assert "weight" in item
        else:
            assert "duration" in item and "heart_rate" in item


def test_recommendation_filters_fatigued_muscles():
    user = User(id="u1", name="User")
    heavy = WeightedSet(
        exercise_name="Dumbbell Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=50,
        ac_weight=50,
        ex_reps=10,
        ac_reps=10,
        pe=PercievedExertion.MAX,
    )
    update_recovery(user, [heavy], timestamp=dt.datetime.utcnow())
    recs = recommend_workout(user, max_exercises=25)
    names = [r["name"] for r in recs] if isinstance(recs, list) else []
    assert "Dumbbell Bench" not in names
    if isinstance(recs, list):
        for item in recs:
            assert "reason" in item and isinstance(item["reason"], str)


def test_recommendation_cardio_removed_when_fatigued():
    user = User(id="u1", name="User")
    run = CardioSession(
        exercise_name="Run",
        ex_duration=60,
        ac_duration=60,
        ex_heart_rate=170,
        ac_heart_rate=170,
        pe=PercievedExertion.HIGH,
    )
    update_recovery(user, [run], timestamp=dt.datetime.utcnow())
    recs = recommend_workout(user, max_exercises=10)
    names = [r["name"] for r in recs] if isinstance(recs, list) else []
    assert "Run" not in names


def test_weekly_targets_scale_with_experience():
    user = User(id="u1", name="User")
    beginner = weekly_fatigue_targets(user)
    user.experience = user.experience.__class__.ADVANCED
    advanced = weekly_fatigue_targets(user)
    assert advanced[Movement.UPPER_PUSH] > beginner[Movement.UPPER_PUSH]


def test_weekly_schedule_respects_allowed_movements():
    user = User(
        id="u2",
        name="User",
        allowed_movements=[Movement.CARDIO, Movement.UPPER_PULL],
    )
    schedule = suggest_weekly_movements(user, workouts_per_week=3)
    for day_moves in schedule.values():
        for m in day_moves:
            assert m in user.allowed_movements
