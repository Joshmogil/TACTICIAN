from pydantic import BaseModel
import datetime as dt
from typing import Dict

from exercise import Exercise
from user import User
from movement import Movement


class Workout(BaseModel):
    date: dt.date
    work_done: 'WorkDone'
    training_effects: Dict[Movement,float] = {}

class WorkDone(BaseModel):
    exercise: Exercise
    amount: float
    intensity: float


def calculate_workout_effects(user: User, workout: Workout) -> Workout:
    #TODO this should user information about the user, as well as information about the workout
    #TODO needs to figure out how much of an effect the workout will have on the user
    
    pass