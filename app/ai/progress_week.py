import json
from app.test import USER
from app.user import User, test_users, interests_prompt
from app.workout import WorkoutDay
from app.ai.tools import parse_workouts
from google import genai
import dotenv
from typing import List, Literal

dotenv.load_dotenv()

ProgressType = Literal["Deload", "Increase", "Decrease","Overload"]

def progress_day(user: User, workout: WorkoutDay, week_goal: ProgressType):

    client = genai.Client()

    difficulty_semantic = ""
    
    match week_goal:
        case "Deload":
            # handle deload logic
            difficulty_semantic = "drastically intensity/volume."
        case "Increase":
            # handle increase logic
            difficulty_semantic = "slightly add intensity/volume."
        case "Decrease":
            # handle decrease logic
            difficulty_semantic = "slightly lower intensity/volume."
        case "Overload":
            # handle overload logic
            difficulty_semantic = "raise intensity/volume to the maximum safe amount."
        case _:
            raise ValueError(f"Unknown ProgressType: {week_goal}")

    prompt=f"""
Response should be comma seperated values
Response should contain just workouts as CSV. No explanations or dialogues.
You are the {interests_prompt(user.interests)} trainer for the following user:
{user.semantic()}

Adjust the following workout to {difficulty_semantic}
{workout.day}:
{workout.workout_df()}

# Make sure to follow the <Week Day>: <Workout as CSV> format, do not include column names
# Always favor decreasing/increasing intensity or amount rather than adding or removing sets, this is less disruptive to the trainee
"""
    print(prompt)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text


if __name__ == "__main__":

    week_num=1

    with open(f"week_{week_num}.json", "r") as f:
        week = json.load(f)
    week=[WorkoutDay(**obj) for obj in week]

    parsed_workouts = []
    for workout in week:
        w = progress_day(user=test_users[USER], workout=workout,week_goal="Increase")
        print(w)
        p = parse_workouts(w)
        parsed_workouts.append(p[0])

    with open(f"week_{week_num+1}.json", "w+") as f:
        json.dump([d.model_dump() for d in parsed_workouts], f, indent=2)