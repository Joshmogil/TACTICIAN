from pydantic import BaseModel
from typing import Literal, Optional
from app.test import USER

Skill = Literal["New","Novice","Intermediate", "Advanced"]


class Range(BaseModel):
    start: int
    end: int

class Interest(BaseModel):
    name: str
    skill: Skill


def get_vigour(age: int, activity_level: int):
    if age < 30 and activity_level == 3:
        return "challenging"
    if age >= 30 and activity_level == 3:
        return "moderately challenging"
    if age >= 55 and activity_level == 2:
        return "cautiously challenging"
    if age < 30 and activity_level == 2:
        return "moderately challenging"
    
def activity_semantic(activity_level:int):

    if activity_level == 1:
        return "inactive"
    
    if activity_level == 2:
        return "moderately active"
    
    if activity_level == 3:
        return "highly active"
    
def interests_prompt(interests: list['Interest']):
    r=""
    for i, interest in enumerate(interests):
        if i < len(interests) -1:
            r = r + f"{interest.name} ({interest.skill})" +", "
        else:
            r = r + f"and {interest.name} ({interest.skill}) "
    return r 

class User(BaseModel):
    name: str
    gender: str
    interests: list[Interest]

    favorite_exercises: list[str]
    age: int 
    activity_level: int # 1-3

    def semantic(self):

        rep=f"""
User: {self.name}
Gender: {self.gender}
Interests: {interests_prompt(self.interests)}
Workouts Per Week: {self.desired_workouts_per_week.start} to {self.desired_workouts_per_week.end}
Favorite Exercises: {[e for e in self.favorite_exercises]}
This user is {self.age} years old and has a {activity_semantic(self.activity_level)} lifestyle, they need {get_vigour(age=self.age, activity_level=self.activity_level)} workouts.
"""
        return rep
test_users={
"josh":User(
        interests=[
            Interest(name="running", skill="Novice"),
            Interest(
                name="lifting weights",
                skill="Intermediate"
                ),
            Interest(
                name="functional strength training",
                skill="Intermediate"
                ),
            Interest(
                name="athleticism",
                skill="Intermediate"
                )
        ],
        desired_workouts_per_week=Range(start=4,end=5),
        favorite_exercises=[
            "jogging",
            "dumbbell benchpress",
            "curl and press",
            "dumbbell lunge"
        ],
        age="27",
        activity_level=2,
        gender="male",
        name="Josh"
    ),

"veronica":User(
        interests=[
            Interest(name="running", skill="Novice"),
            Interest(
                name="lifting-weights",
                skill="Intermediate"
                )
        ],
        desired_workouts_per_week=Range(start=4,end=5),
        favorite_exercises=[
            "jogging",
            "dumbbell benchpress",
            "curl and press",
            "dumbbell lunge"
        ],
        age="55",
        activity_level=2,
        gender="female",
        name="Veronica"
    ),

"spencer":User(
        interests=[
            Interest(name="Running", skill="Advanced"),
            Interest(
                name="Rock Climbing",
                skill="Advanced"
                )
        ],
        desired_workouts_per_week=Range(start=4,end=5),
        favorite_exercises=[
        ],
        age="28",
        activity_level=2,
        gender="male",
        name="Spencer"
    )
}
if __name__ == "__main__":

    print(test_users[USER].model_dump_json())
    print(test_users[USER].semantic())
    print(interests_prompt(test_users[USER].interests))