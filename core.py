from enum import Enum
from math import exp
from typing import List, Literal, Union

from pydantic import BaseModel


class Movement(str, Enum):
    UPPER_PUSH = "upper_push"
    UPPER_PULL = "upper_pull"
    LOWER_PUSH = "lower_push"
    LOWER_PULL = "lower_pull"
    CORE = "core"
    CARDIO = "cardio"
    FUNCTIONAL = "functional"
    LOWER_PLYO = "lower_plyo"
    UPPER_PLYO = "upper_plyo"


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


class PercievedExertion(str, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MAX = 4


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
    ex_weight: float  # kg
    ac_weight: float
    ex_reps: int
    ac_reps: int

    pe: PercievedExertion

    @property
    def workload(self) -> float:
        """Estimate workload using actual values and perceived effort."""
        weight = self.ac_weight if self.ac_weight else self.ex_weight
        reps = self.ac_reps if self.ac_reps else self.ex_reps
        # scale tonnage by perceived exertion on a 0-1 range
        intensity = int(self.pe.value) / int(PercievedExertion.MAX.value)
        return weight * reps * intensity


class CardioSession(BaseModel):
    type: Literal["cardio"] = "cardio"
    exercise_name: str
    pattern: Movement = Movement.CARDIO
    ex_duration: float  # minutes
    ac_duration: float
    ex_heart_rate: int  # avg bpm
    ac_heart_rate: int

    pe: PercievedExertion

    @property
    def workload(self) -> float:
        """
        Banister TRIMP (very rough):
        duration(min) * ΔHR_ratio * exp(1.92 * ΔHR_ratio)
        ΔHR_ratio = (HRavg − HRrest)/(HRmax − HRrest)
        For demo we'll assume HRrest=60, HRmax=190.
        """
        duration = self.ac_duration if self.ac_duration else self.ex_duration
        heart_rate = self.ac_heart_rate if self.ac_heart_rate else self.ex_heart_rate
        hr_ratio = (heart_rate - 60) / (190 - 60)
        trimp = duration * hr_ratio * exp(1.92 * hr_ratio)
        intensity = int(self.pe.value) / int(PercievedExertion.MAX.value)
        return trimp * intensity


# discriminated union for runtime parsing
WorkDone = Union[WeightedSet, CardioSession]


from collections import defaultdict
from typing import Dict, Iterable


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
        ex_duration=20,
        ac_duration=20,
        ex_heart_rate=170,
        ac_heart_rate=185,
        pe=PercievedExertion.HIGH,
    )
    bench = WeightedSet(
        exercise_name="Bench Press",
        pattern=Movement.UPPER_PUSH,
        ex_weight=100,
        ac_weight=100,
        ex_reps=5,
        ac_reps=5,
        pe=PercievedExertion.HIGH,
    )

    today: List[WorkDone] = [bench, run]
    summary = aggregate_workload(today)
    print(summary)
    # → {Movement.UPPER_PUSH: 375.0, Movement.CARDIO: 91.38}
