from pydantic import BaseModel
from movement import Movement
from typing import List, Union

class RangeFactor(BaseModel):
    gt: float = 0 #greater than
    lt_et: float = 1 #less than
    factor: float = 0  #TODO must be between 0 and 1

class TrainingCurve(BaseModel):
    amount_range_factors: List[RangeFactor] 
    intensity_range_factors: List[RangeFactor]
    #TODO amount_range_factors cannot overlap
    #TODO intensity_range_factors cannot overlap

    def _get_amount_factor(self, amount: Union[float, int]):
        amount=float(amount)
        for range in self.amount_range_factors:
            if amount > range.gt and amount <= range.lt_et:
                return range.factor
    
    def _get_intensity_factor(self, intensity: Union[float, int]):
        intensity=float(intensity)
        for range in self.intensity_range_factors:
            if intensity > range.gt and intensity <= range.lt_et:
                return range.factor

class Train(BaseModel):
    movement: Movement
    training_curve: TrainingCurve

class Exercise(BaseModel):
    name: str
    trains: List[Train]