import app.db
import json
from app.test import USER
from app.user import UserInfo, test_users, interests_prompt, UserFeedback
from app.workout import WorkoutDay, WorkoutWeek
from app.ai.tools import parse_workouts
from google import genai
import dotenv
from typing import List, Literal
from app.ai.models import FLASH, PRO, MODEL


dotenv.load_dotenv()

ProgressType = Literal["Deload", "Increase", "Decrease","Overload"]

def progress_day(user: UserInfo, workout: WorkoutDay, week_goal: ProgressType):

    client = genai.Client()

    difficulty_semantic = ""
    
    match week_goal:
        case "Deload":
            # handle deload logic
            difficulty_semantic = "drastically decrease intensity/volume."
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
        model=MODEL, contents=prompt
    )
    return response.text

def progress_week(user: UserInfo, week: WorkoutWeek, feedback: UserFeedback, week_goal: ProgressType):
    client = genai.Client()

    difficulty_semantic = ""
    
    match week_goal:
        case "Deload":
            # handle deload logic
            difficulty_semantic = "drastically decrease intensity/volume."
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



Workouts are in the following format:
{WorkoutDay.example()}

Overall, adjust the user's previous week to {difficulty_semantic}

# Make sure to follow the <Week Day>: <Workout as CSV> format, do not include column names
# Make sure to use the same week days from the previosue week
# Remove/add exercises as needed to accomodate the user's feedback
# Pay special attention to the user opinion on their interests and feedback on muscle groups
# When adding or removing things, try to keep the same number of sets and reps as the previous week
# Feel free to add new exercises, but make sure they are relevant to the user, 

The user has the following feedback for the week:
{feedback.semantic()}

User's Previous week:
{week.semantic()}
"""
    print(prompt)
    
    response = client.models.generate_content(
        model=MODEL, contents=prompt
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