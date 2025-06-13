import datetime as dt

from app.models import User
from app.recommendation import recommend_workout, recommend_movements
from app.recovery import update_recovery
from core import CardioSession, Movement, PercievedExertion, WeightedSet


def test_recommendation_ranks_by_intensity():
    user = User(id="u1", name="User")
    ws1 = WeightedSet(
        exercise_name="Dumbbell Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=20,
        ac_weight=20,
        ex_reps=5,
        ac_reps=5,
        pe=PercievedExertion.HIGH,
    )
    ws2 = WeightedSet(
        exercise_name="Dumbbell Row",
        pattern=Movement.UPPER_PULL,
        ex_weight=20,
        ac_weight=20,
        ex_reps=5,
        ac_reps=5,
        pe=PercievedExertion.MEDIUM,
    )
    update_recovery(user, [ws1, ws2], timestamp=dt.datetime.utcnow())
    recs = recommend_workout(user, max_exercises=50)
    names = [r["name"] for r in recs]
    assert "Dumbbell Row" in names
    assert "Dumbbell Bench" in names
    assert names.index("Dumbbell Row") < names.index("Dumbbell Bench")
    row = next(r for r in recs if r["name"] == "Dumbbell Row")
    bench = next(r for r in recs if r["name"] == "Dumbbell Bench")
    assert row["weight"] == 20
    assert row["reps"] == 5
    assert bench["weight"] == 20
    assert bench["reps"] == 5


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


def test_recommendation_ranks_cardio_history():
    user = User(id="u1", name="User")
    run = CardioSession(
        exercise_name="Run",
        ex_duration=30,
        ac_duration=30,
        ex_heart_rate=170,
        ac_heart_rate=170,
        pe=PercievedExertion.HIGH,
    )
    update_recovery(user, [run], timestamp=dt.datetime.utcnow())
    recs = recommend_workout(user, max_exercises=25)
    names = [r["name"] for r in recs]
    assert "Jump Rope" in names
    assert "Run" in names
    assert names.index("Jump Rope") < names.index("Run")
    run_rec = next(r for r in recs if r["name"] == "Run")
    assert run_rec["duration"] == 30
    assert run_rec["heart_rate"] == 170
