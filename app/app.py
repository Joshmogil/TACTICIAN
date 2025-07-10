from fastapi import FastAPI
from app.workout import WorkoutDay, WorkDone
from app.ai import first_week

from typing import List

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the TACTICIAN API!"}

@app.get("/week", response_model=List[WorkoutDay])
def get_first_week():
    # Example data
    week = [
        WorkoutDay(
            day="Monday",
            workout=[
                WorkDone(
                    exercise="Run",
                    amount=30.0,
                    actual_amount=30.0,
                    amount_unit="min",
                    intensity=140.0,
                    actual_intensity=135.0,
                    intensity_unit="bpm",
                    perceived_exertion=6
                )
            ]
        )
    ]
    return week