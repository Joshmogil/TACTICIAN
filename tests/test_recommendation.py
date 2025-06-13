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
    assert "Dumbbell Row" in recs
    assert "Dumbbell Bench" in recs
    assert recs.index("Dumbbell Row") < recs.index("Dumbbell Bench")


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
    assert "Dumbbell Bench" not in recs


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
    assert "Jump Rope" in recs
    assert "Run" in recs
    assert recs.index("Jump Rope") < recs.index("Run")


def test_recommend_movements_returns_all_when_fresh():
    user = User(id="u1", name="User")
    moves = recommend_movements(user)
    assert set(m.value for m in moves) == set(m.value for m in Movement)
