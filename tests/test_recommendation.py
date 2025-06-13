import datetime as dt

from app.models import User
from app.recovery import update_recovery
from app.recommendation import recommend_workout
from core import WeightedSet, Movement, PercievedExertion


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

