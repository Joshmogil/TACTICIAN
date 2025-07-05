from pydantic import BaseModel
from typing import Literal

TYPES_OF_EXERCISES = [
    "strength",
    "cardio",
    "plyometric",
    "swimming",
    "running"
]

class ExerciseFeature(BaseModel):
    name: str
    value: str
    specificity: str