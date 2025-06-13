import datetime as dt

from app.models import User
from app.recovery import update_recovery
from core import WeightedSet, Movement, PercievedExertion
from workout import load_workout_data


def test_recovery_update_and_decay():
    user = User(id="u1", name="User")
    ws = WeightedSet(
        exercise_name="Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=100,
        ac_weight=100,
        ex_reps=5,
        ac_reps=5,
        pe=PercievedExertion.HIGH,
    )
    t1 = dt.datetime(2024, 1, 1, 12, 0)
    update_recovery(user, [ws], timestamp=t1)
    # initial load
    assert user.recovery.scores[Movement.UPPER_PUSH] == ws.workload

    # after 48 hours scores should decay by half
    t2 = t1 + dt.timedelta(hours=48)
    update_recovery(user, [], timestamp=t2)
    assert user.recovery.scores[Movement.UPPER_PUSH] == ws.workload * 0.5


def test_load_workout_data_pipeline():
    workouts = load_workout_data()
    # we expect all csv files to be loaded
    assert len(workouts) >= 4
    for w in workouts.values():
        assert len(w.work_done) > 0
        # check that totals returns a mapping with movements
        assert isinstance(w.totals, dict)
