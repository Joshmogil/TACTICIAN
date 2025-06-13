import math
from core import (
    WeightedSet,
    CardioSession,
    Movement,
    PercievedExertion,
    Exercise,
    MuscleUsage,
    MuscleQuality,
    Muscle,
    aggregate_workload,
    aggregate_muscle_workload,
)
from load_exercises import load_exercises


def test_weightedset_workload():
    ws = WeightedSet(
        exercise_name="Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=100,
        ac_weight=120,
        ex_reps=8,
        ac_reps=6,
        pe=PercievedExertion.HIGH,
    )
    expected = 120 * 6 * (int(PercievedExertion.HIGH.value) / int(PercievedExertion.MAX.value))
    assert ws.workload == expected


def test_cardiosession_workload():
    cs = CardioSession(
        exercise_name="Run",
        ex_duration=20,
        ac_duration=20,
        ex_heart_rate=170,
        ac_heart_rate=180,
        pe=PercievedExertion.MEDIUM,
    )
    hr_ratio = (180 - 60) / (190 - 60)
    trimp = 20 * hr_ratio * math.exp(1.92 * hr_ratio)
    expected = trimp * (int(PercievedExertion.MEDIUM.value) / int(PercievedExertion.MAX.value))
    assert math.isclose(cs.workload, expected, rel_tol=1e-6)


def test_aggregate_workload():
    ws = WeightedSet(
        exercise_name="Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=100,
        ac_weight=100,
        ex_reps=5,
        ac_reps=5,
        pe=PercievedExertion.HIGH,
    )
    cs = CardioSession(
        exercise_name="Run",
        ex_duration=30,
        ac_duration=30,
        ex_heart_rate=170,
        ac_heart_rate=170,
        pe=PercievedExertion.LOW,
    )
    totals = aggregate_workload([ws, cs])
    expected_ws = ws.workload
    expected_cs = cs.workload
    assert totals[Movement.UPPER_PUSH] == expected_ws
    assert totals[Movement.CARDIO] == expected_cs


def test_aggregate_muscle_workload():
    raw_ex = load_exercises()
    # only convert the exercise needed for this test
    exercises = {"Dumbbell Bench": Exercise(**raw_ex["Dumbbell Bench"])}
    ws = WeightedSet(
        exercise_name="Dumbbell Bench",
        pattern=Movement.UPPER_PUSH,
        ex_weight=100,
        ac_weight=100,
        ex_reps=10,
        ac_reps=10,
        pe=PercievedExertion.HIGH,
    )
    muscles = aggregate_muscle_workload([ws], exercises)
    base = ws.workload
    ex_info = exercises["Dumbbell Bench"]
    for usage in ex_info.muscles:
        expected = base * usage.amount
        assert math.isclose(muscles[usage.muscle], expected, rel_tol=1e-6)
