from pydantic import BaseModel
from enum import Enum
from typing import Union, Literal, List
from math import exp

class Movement(str, Enum):
    UPPER_PUSH = "upper_push"
    UPPER_PULL = "upper_pull"
    LOWER_PUSH = "lower_push"
    LOWER_PULL = "lower_pull"
    CORE = "core"
    CARDIO = "cardio"

class Muscle(str, Enum):
    LATS = "lats"
    CHEST = "chest"
    FRONT_DELTS = "front_shoulder"
    MEDIAL_DELTS = "medial_delts"
    REAR_DELTS = "rear_delts"
    TRAPS = "traps"
    TRICEPS = "triceps"
    BICEPS = "biceps"
    FOREARMS = "forearms"
    ABS = "abs"
    OBLIQUES = "obliques"
    LOWERBACK = "lowerback"
    UPPER_BACK = "upper_back"
    GLUTES = "glutes"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    CALFS = "calfs"

class MuscleQuality(str, Enum):
    ENERGY = "energy"
    STRENGTH = "strength"


class MuscleUsage(BaseModel):
    muscle: Muscle
    amount: float
    quality: MuscleQuality


class Exercise(BaseModel):
    name: str
    movement: Movement
    muscles: List[MuscleUsage]


class WeightedSet(BaseModel):
    type: Literal["weighted"] = "weighted"
    exercise_name: str
    pattern: Movement
    weight: float  # kg
    reps: int

    @property
    def workload(self) -> float:
        """Simple tonnage metric (kg‑reps)."""
        return self.weight * self.reps


class CardioSession(BaseModel):
    type: Literal["cardio"] = "cardio"
    exercise_name: str
    pattern: Movement = Movement.CARDIO
    duration: float          # minutes
    heart_rate: int          # avg bpm

    @property
    def workload(self) -> float:
        """
        Banister TRIMP (very rough):
        duration(min) * ΔHR_ratio * exp(1.92 * ΔHR_ratio)
        ΔHR_ratio = (HRavg − HRrest)/(HRmax − HRrest)
        For demo we'll assume HRrest=60, HRmax=190.
        """
        hr_ratio = (self.heart_rate - 60) / (190 - 60)
        return self.duration * hr_ratio * exp(1.92 * hr_ratio)


# discriminated union for runtime parsing
WorkDone = Union[WeightedSet, CardioSession]



from collections import defaultdict
from typing import Iterable, Dict

def aggregate_workload(work: Iterable[WorkDone]) -> Dict[Movement, float]:
    """
    Sum workload by movement pattern.
    If pattern is CARDIO or CORE that’s fine—they get their own bucket.
    """
    tally: Dict[Movement, float] = defaultdict(float)
    for w in work:
        tally[w.pattern] += w.workload
    return dict(tally)

if __name__ == "__main__":
    run = CardioSession(
    exercise_name="Run",
    duration=20,
    heart_rate=185
    )
    bench = WeightedSet(
        exercise_name="Bench Press",
        pattern=Movement.UPPER_PUSH,
        weight=100,
        reps=5
    )

    today = [bench, run]
    summary = aggregate_workload(today)
    print(summary)
    # → {Movement.UPPER_PUSH: 500.0, Movement.CARDIO: 119.3}

