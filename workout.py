import datetime as dt
import os
import re
from typing import Dict, List
from collections import defaultdict

import pandas as pd
from pydantic import BaseModel

from core import (
    CardioSession,
    Movement,
    PercievedExertion,
    WeightedSet,
    WorkDone,
    aggregate_workload,
)
from load_exercises import load_exercises
import datetime


class Workout(BaseModel):
    date: dt.date
    user_id: str = "default"
    work_done: List[WorkDone]

    @property
    def totals(self) -> Dict[Movement, float]:
        return aggregate_workload(self.work_done)


WORKOUT_HISTORY: Dict[str, List[Workout]] = defaultdict(list)


def _parse_date(date_str):
    """Convert date string like '6-9-2025' to datetime.date object"""
    try:
        return datetime.datetime.strptime(date_str, "%m-%d-%Y").date()
    except ValueError:
        print(f"Error parsing date: {date_str}")
        return None


def _canon(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


def _parse_number(val) -> float:
    if pd.isna(val):
        return 0.0
    m = re.search(r"[-+]?(\d*\.?\d+)", str(val))
    return float(m.group(1)) if m else 0.0


def _parse_int(val) -> int:
    return int(round(_parse_number(val)))


def _parse_pe(val) -> PercievedExertion:
    n = _parse_number(val)
    if not n:
        return PercievedExertion.MEDIUM
    n = max(1, min(4, int(round(n))))
    return PercievedExertion(str(n))


def df_to_workout(date: datetime.date, df: pd.DataFrame, user_id: str = "default") -> Workout:
    exercises = load_exercises()
    lookup = {_canon(k): k for k in exercises}
    lookup["windshieldwhipers"] = "Windshield Wipers"

    work_items: List[WorkDone] = []
    current_ex = None

    for _, row in df.iterrows():
        raw_name = row.get("exercise")
        if isinstance(raw_name, str) and raw_name.strip():
            current_ex = raw_name.strip()
        elif current_ex is None:
            continue

        if current_ex is None:
            continue

        canon = _canon(current_ex)
        if canon not in lookup:
            continue
        ex_name = lookup[canon]
        ex_info = exercises[ex_name]
        movement = Movement(ex_info["movement"])

        pe = _parse_pe(row.get("perceived exertion"))

        if movement == Movement.CARDIO:
            item = CardioSession(
                exercise_name=ex_name,
                pattern=movement,
                ex_duration=_parse_number(row.get("number")),
                ac_duration=_parse_number(row.get("actual")),
                ex_heart_rate=_parse_int(row.get("intensity")),
                ac_heart_rate=_parse_int(row.get("actual.1")),
                pe=pe,
            )
        else:
            item = WeightedSet(
                exercise_name=ex_name,
                pattern=movement,
                ex_weight=_parse_number(row.get("intensity")),
                ac_weight=_parse_number(row.get("actual.1")),
                ex_reps=_parse_int(row.get("number")),
                ac_reps=_parse_int(row.get("actual")),
                pe=pe,
            )
        work_items.append(item)

    workout = Workout(date=date, user_id=user_id, work_done=work_items)
    WORKOUT_HISTORY[user_id].append(workout)
    return workout


def load_workout_data(directory="_Workouts", user_id: str = "default"):
    workout_data = {}

    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return workout_data

    files = os.listdir(directory)
    csv_files = [f for f in files if f.endswith(".csv")]

    if not csv_files:
        print(f"No CSV files found in '{directory}'.")
        return workout_data

    for file in csv_files:
        file_path = os.path.join(directory, file)
        try:
            df = pd.read_csv(file_path)
            filename = os.path.splitext(file)[0]
            workout_data[filename] = df_to_workout(
                date=_parse_date(filename),
                df=df,
                user_id=user_id,
            )
            print(f"Loaded: {filename} ({len(df)} rows)")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

    return workout_data


workouts = load_workout_data()

if __name__ == "__main__":
    for name, item in workouts.items():
        print(f"\nWorkout: {name}")
        print(item)
