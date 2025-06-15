from pydantic import BaseModel
from enum import Enum
import datetime as dt
from typing import List

class UserMovement(BaseModel):
    name: str
    current_fatigue: float = 0
    current_capacity: float = 0
    
class FatigueSchedule:
    movement: 'Movement'
    day_targs: List['FatigueTarget'] #TODO: list should be 1-7 in length
    week_targs: List['FatigueTarget'] #TODO: list should be 4-5 in length
    month_targs: List['FatigueTarget'] #TODO: list should be 3 in length
    quarter_targs: List['FatigueTarget'] #TODO: list should be 4 in length
    yearly_target: 'FatigueTarget' 

class FatigueTarget:
    date: dt.date
    target: float
    

class Movement(Enum):
    LOWER_PULL = "lower_pull"
    LOWER_PUSH = "lower_push"
    VERTICAL_JUMP = "vertical_jump"
    LATERAL_BOUND = "lateral_bound"
    FORWARD_LEAP = "forward_leap"
    LOWER_CARDIO = "lower_cardio"
    UPPER_VERTICAL_PUSH = "upper_vertical_push"
    UPPER_HORIZONTAL_PUSH = "upper_horizontal_push"
    UPPER_VERTICAL_PULL = "upper_vertical_pull"
    UPPER_HORIZONTAL_PULL = "upper_horizontal_pull"
    EXPLOSIVE_UPPER_PUSH = "explosive_upper_push"
    EXPLOSIVE_UPPER_PULL = "explosive_upper_pull"
    THROW = "throw"
    UPPER_CARDIO = "upper_cardio"
    HIP_HINGE = "hip_hinge"
    HIP_TUCK = "hip_tuck"
    SPINAL_FLEXION = "spinal_flexion"
    SPINAL_EXTENSION = "spinal_extension"
    SPINAL_STABILIZATION = "spinal_stabilization"
    SPINAL_LATERAL = "spinal_lateral"
    SPINAL_ROTATION = "spinal_rotation"

# Update the dictionary to use the enum
MOVEMENTS_DICT = {m.value: UserMovement(name=m.value) for m in Movement}

print(MOVEMENTS_DICT)