import datetime as dt
import os
import re
from typing import List

import pandas as pd
from pydantic import BaseModel

from core import CardioSession, Movement, PercievedExertion, WeightedSet, WorkDone
from load_exercises import load_exercises


class Workout(BaseModel):
    date: dt.date
    work_done: List[WorkDone]


def _canon(name: str) -> str:
    """Return a normalised key for exercise lookups."""
    return re.sub(r"[^a-z]", "", name.lower())


def _parse_number(val) -> float:
    """Extract a float from a messy cell value."""
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
    return PercievedExertion(n)


def df_to_workout(df: pd.DataFrame) -> Workout:
    """Convert a raw workout CSV ``DataFrame`` into a ``Workout`` model."""

    exercises = load_exercises()
    lookup = {_canon(k): k for k in exercises}
    # manual typo corrections
    lookup["windshieldwhipers"] = "Windshield Wipers"

    work_items: List[WorkDone] = []
    current_ex = None

    for _, row in df.iterrows():
        raw_name = row.get("exercise")
        if isinstance(raw_name, str) and raw_name.strip():
            current_ex = raw_name.strip()
        elif current_ex is None:
            # nothing to propagate
            continue

        if current_ex is None:
            continue

        canon = _canon(current_ex)
        if canon not in lookup:
            # unknown exercise, skip row
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

    return Workout(date=dt.date.today(), work_done=work_items)


def load_workout_data(directory="_Workouts"):
    """
    Load all CSV files from the specified directory into pandas DataFrames

    Args:
        directory (str): Path to the directory containing workout files

    Returns:
        dict: Dictionary mapping filenames to pandas DataFrames
    """
    workout_data = {}

    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return workout_data

    # List all files in directory
    files = os.listdir(directory)

    # Filter for CSV files
    csv_files = [f for f in files if f.endswith(".csv")]

    if not csv_files:
        print(f"No CSV files found in '{directory}'.")
        return workout_data

    # Read each CSV file into a DataFrame
    for file in csv_files:
        file_path = os.path.join(directory, file)
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)

            # Store DataFrame with filename (without extension) as key
            filename = os.path.splitext(file)[0]
            workout_data[filename] = df

            print(f"Loaded: {filename} ({len(df)} rows)")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

    return workout_data


# Load all workout files
workouts = load_workout_data()


# Example: Access a specific workout by name
# If you have a file "_Workouts/Running_Log.csv", access it with:
# running_df = workouts["Running_Log"]

# Example: Process all workouts
for name, df in workouts.items():
    print(f"\nWorkout: {name}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {', '.join(df.columns)}")
