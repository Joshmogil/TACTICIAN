from pydantic import BaseModel
from typing import Literal, Optional, List
from app.test import USER

Skill = Literal["New","Novice","Intermediate", "Advanced"]

ActivityLevel = Literal["Inactive","Active", "Highly Active"]

MuscleReportOption = Literal["Not enough", "Just right", "Too much"]

InterestReportOption = Literal[
    "Perfect As Is",
    "More exercise variety",
    "Less exercise variety",
    "More difficulty",
    "Less difficulty",
    "More volume",
    "Less volume",
    "More often",
    "Less often"
]

UserSpecialRequest = Literal[Literal["Josh"], Literal["Brother"]]

class Range(BaseModel):
    start: int
    end: int

class Interest(BaseModel):
    name: str
    skill: Skill


def get_vigour(age: int, activity_level: ActivityLevel) -> str:
    if age < 30 and activity_level == "Highly Active":
        return "challenging"
    if age >= 30 and activity_level == "Highly Active":
        return "moderately challenging"
    if age >= 55 and activity_level == "Active":
        return "cautiously challenging"
    if age < 30 and activity_level == "Active":
        return "moderately challenging"
    
def activity_semantic(activity_level:ActivityLevel):

    if activity_level == "Inactive":
        return "inactive"
    
    if activity_level == "Active":
        return "moderately active"
    
    if activity_level ==  "Highly Active":
        return "highly active"
    
def interests_prompt(interests: list['Interest']):
    r=""
    for i, interest in enumerate(interests):
        if i < len(interests) -1:
            r = r + f"{interest.name} ({interest.skill})" +", "
        else:
            r = r + f"and {interest.name} ({interest.skill}) "
    return r 


class UserInfo(BaseModel):
    name: str
    gender: str
    interests: list[Interest]

    desired_workouts_per_week: Range

    favorite_exercises: list[str]
    age: int 
    activity_level: ActivityLevel

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
    
class UserFeedback(BaseModel):
    biceps: MuscleReportOption = "Just right"
    triceps: MuscleReportOption = "Just right"
    forearms: MuscleReportOption = "Just right"
    hands: MuscleReportOption = "Just right"
    rear_deltoids: MuscleReportOption = "Just right"
    middle_deltoids: MuscleReportOption = "Just right"
    front_deltoids: MuscleReportOption = "Just right"
    upper_chest: MuscleReportOption = "Just right"
    chest: MuscleReportOption = "Just right"
    traps: MuscleReportOption = "Just right"
    upper_back: MuscleReportOption = "Just right"
    lats: MuscleReportOption = "Just right"
    abs: MuscleReportOption = "Just right"
    obliques: MuscleReportOption = "Just right"
    lower_back: MuscleReportOption = "Just right"
    glutes: MuscleReportOption = "Just right"
    hamstrings: MuscleReportOption = "Just right"
    quads: MuscleReportOption = "Just right"
    calves: MuscleReportOption = "Just right"

    interest_reports: dict[str, List[InterestReportOption]]

    def semantic(self) -> str:
        
        mr = ""
        if self.biceps == "Too much":
            mr += "Decrease bicep workload\n"
        if self.biceps == "Not enough":
            mr += "Increase bicep workload\n"
        if self.triceps == "Too much":
            mr += "Decrease tricep workload\n"
        if self.triceps == "Not enough":
            mr += "Increase tricep workload\n"
        if self.forearms == "Too much":
            mr += "Decrease forearm workload\n"
        if self.forearms == "Not enough":
            mr += "Increase forearm workload\n"
        if self.hands == "Too much":
            mr += "Decrease hand workload\n"
        if self.hands == "Not enough":
            mr += "Increase hand workload\n"
        if self.rear_deltoids == "Too much":
            mr += "Decrease rear deltoid workload\n"
        if self.rear_deltoids == "Not enough":
            mr += "Increase rear deltoid workload\n"
        if self.middle_deltoids == "Too much":
            mr += "Decrease middle deltoid workload\n"
        if self.middle_deltoids == "Not enough":
            mr += "Increase middle deltoid workload\n"
        if self.front_deltoids == "Too much":
            mr += "Decrease front deltoid workload\n"
        if self.front_deltoids == "Not enough":
            mr += "Increase front deltoid workload\n"
        if self.upper_chest == "Too much":
            mr += "Decrease upper chest workload\n"
        if self.upper_chest == "Not enough":
            mr += "Increase upper chest workload\n"
        if self.chest == "Too much":
            mr += "Decrease chest workload\n"
        if self.chest == "Not enough":
            mr += "Increase chest workload\n"
        if self.traps == "Too much":
            mr += "Decrease trap workload\n"
        if self.traps == "Not enough":
            mr += "Increase trap workload\n"
        if self.upper_back == "Too much":
            mr += "Decrease upper back workload\n"
        if self.upper_back == "Not enough":
            mr += "Increase upper back workload\n"
        if self.lats == "Too much":
            mr += "Decrease lat workload\n"
        if self.lats == "Not enough":
            mr += "Increase lat workload\n"
        if self.abs == "Too much":
            mr += "Decrease ab workload\n"
        if self.abs == "Not enough":
            mr += "Increase ab workload\n"
        if self.obliques == "Too much":
            mr += "Decrease oblique workload\n"
        if self.obliques == "Not enough":
            mr += "Increase oblique workload\n"
        if self.lower_back == "Too much":
            mr += "Decrease lower back workload\n"
        if self.lower_back == "Not enough":
            mr += "Increase lower back workload\n"
        if self.glutes == "Too much":
            mr += "Decrease glute workload\n"
        if self.glutes == "Not enough":
            mr += "Increase glute workload\n"
        if self.hamstrings == "Too much":
            mr += "Decrease hamstring workload\n"
        if self.hamstrings == "Not enough":
            mr += "Increase hamstring workload\n"
        if self.quads == "Too much":
            mr += "Decrease quad workload\n"
        if self.quads == "Not enough":
            mr += "Increase quad workload\n"
        if self.calves == "Too much":
            mr += "Decrease calf workload\n"
        if self.calves == "Not enough":
            mr += "Increase calf workload\n"
        
        interests_semantic = ""
        for interest, reports in self.interest_reports.items():
            formatted_reports = ", ".join(reports)
            interests_semantic += f"{interest}: {formatted_reports}\n"

        return f"""
{mr}

User opinion on interests:
{interests_semantic}
"""


test_users={
"josh":UserInfo(
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
        activity_level="Active",
        gender="male",
        name="Josh"
    ),

"veronica":UserInfo(
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
        activity_level="Active",
        gender="female",
        name="Veronica"
    ),

"spencer":UserInfo(
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
        activity_level="Highly Active",
        gender="male",
        name="Spencer"
    )
}
if __name__ == "__main__":

    print(test_users[USER].model_dump_json())
    print(test_users[USER].semantic())
    print(interests_prompt(test_users[USER].interests))
