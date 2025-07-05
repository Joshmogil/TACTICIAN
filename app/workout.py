from pydantic import BaseModel
import pandas as pd
from typing import Literal, Optional, List


WeekDay = Literal["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

class WorkDone(BaseModel):
    exercise: str 
    amount: float
    actual_amount: float
    amount_unit: str
    intensity: float
    actual_intensity: float
    intensity_unit: str
    perceived_exertion: Optional[str]

def workout_as_dataframe(workdone_list: List[WorkDone]) -> pd.DataFrame:
    """Convert a list of WorkDone objects to a pandas DataFrame."""
    if not workdone_list:
        return pd.DataFrame()  # Return an empty DataFrame if the list is empty

    # Convert each WorkDone object to a 
    data=[]
    for work in workdone_list:
        data.append(work.model_dump())

    # Create the DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    return df

def dataframe_to_workdone_list(df: pd.DataFrame) -> List[WorkDone]:
    """Convert a pandas DataFrame to a list of WorkDone objects."""
    workdone_list = []
    for _, row in df.iterrows():
        try:
            workdone = WorkDone(**row.to_dict())
            workdone_list.append(workdone)
        except Exception as e:
            print(f"Error creating WorkDone object from row: {row.to_dict()}. Error: {e}")
            # Handle the error as needed, e.g., skip the row or raise an exception
    return workdone_list


class WorkoutDay(BaseModel):
    day: WeekDay
    workout: List[WorkDone]

    def workout_df(self):
        return workout_as_dataframe(self.workout)

    def semantic(self):
        # Use tabulate for prettier tables if you want, or stick with pandas
        df_str = self.workout_df().to_string(index=False)
        rep = f"{self.day}:\n{df_str}\n"
        return rep
    
    @staticmethod
    def example():
        return """Example:
Monday:
           exercise  amount  actual_amount amount_unit  intensity  actual_intensity intensity_unit  perceived_exertion
0               Foo    24.0           24.0         min      165.0               0.0            bpm                None
1               Bar     8.0            5.0        reps        200               0.0            lbs                 Low
2               Bar     8.0            5.0        reps        200               0.0            lbs                None
3               Bar     8.0            5.0        reps        200               0.0            lbs                High
4               Fizz   12.0           10.0        reps        0.0               0.0           None              Medium
5               Buzz   20.0           20.0        reps        0.0               0.0            lbs                 Low

# Workouts can have anywhere from 5-30 sets.
# Workouts should be challenging and attempt to vary exercises
# Make sure to account differences between genders (Male and Female)
# Make sure to adjust the intensity of exercises appropriately for the age, gender, and skill level
# 
"""
        
    

if __name__ == "__main__":

    # Updated data: include amount_unit and intensity_unit
    workdone_list = [
        WorkDone(
            exercise="Run",
            amount=24.0,
            actual_amount=24.0,
            amount_unit="min",
            intensity=165.0,
            actual_intensity=160.0,
            intensity_unit="bpm",
            perceived_exertion=7
        ),
        WorkDone(
            exercise="Staircase Pullup",
            amount=8.0,
            actual_amount=5.0,
            amount_unit="reps",
            intensity=0.0,
            actual_intensity=0.0,
            intensity_unit="",
            perceived_exertion=8
        ),
        WorkDone(
            exercise="Pole Press",
            amount=12.0,
            actual_amount=10.0,
            amount_unit="reps",
            intensity=0.0,
            actual_intensity=0.0,
            intensity_unit="",
            perceived_exertion=7
        ),
        WorkDone(
            exercise="Vertical hops",
            amount=20.0,
            actual_amount=20.0,
            amount_unit="reps",
            intensity=0.0,
            actual_intensity=0.0,
            intensity_unit="",
            perceived_exertion=6
        ),
    ]
    print(WorkoutDay(day="Monday", workout=workdone_list).semantic())
    print(WorkoutDay.example())
