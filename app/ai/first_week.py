from google import genai
import dotenv
from app.workout import WorkoutDay, WorkDone
from app.user import UserInfo, test_users, interests_prompt
from app.test import USER
from app.ai.tools import parse_workouts
from typing import List

dotenv.load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.

def generate_raw_week(user: UserInfo):
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=f"""
Response should be comma seperated values
Response should contain just workouts as CSV. No explanations or dialogues.
You are the {interests_prompt(user.interests)} trainer for the following user:
{user.semantic()}
Create a week's (total {user.desired_workouts_per_week.start} to {user.desired_workouts_per_week.end}) worth of workouts in the following format:
{WorkoutDay.example()}

# Make sure to follow the <Week Day>: <Workout as CSV> format, do not include column names
# Make sure to balance exercises across days
# Make sure to include exercises and activities that satisfy all of the user's interests
# Try to put your self into the shoes of the user, workouts should have a logical rythym and flow

"""
    )
    return response.text


# Example usage:
if __name__ == "__main__":
    day_g = generate_raw_week(test_users[USER])
    #print(day)
    day="""
Monday:
Easy Run,15.0,15.0,min,145.0,0.0,bpm,0
Dynamic Stretching,5.0,5.0,min,0.0,0.0,None,0
800m Interval,800.0,800.0,m,178.0,0.0,bpm,0
Recovery Jog,400.0,400.0,m,130.0,0.0,bpm,0
800m Interval,800.0,800.0,m,178.0,0.0,bpm,0
Recovery Jog,400.0,400.0,m,130.0,0.0,bpm,0
800m Interval,800.0,800.0,m,178.0,0.0,bpm,0
Recovery Jog,400.0,400.0,m,130.0,0.0,bpm,0
800m Interval,800.0,800.0,m,178.0,0.0,bpm,0
Recovery Jog,400.0,400.0,m,130.0,0.0,bpm,0
800m Interval,800.0,800.0,m,178.0,0.0,bpm,0
Recovery Jog,400.0,400.0,m,130.0,0.0,bpm,0
Cool Down Run,10.0,10.0,min,135.0,0.0,bpm,0
Plank,60.0,60.0,sec,0.0,0.0,None,0
Plank,60.0,60.0,sec,0.0,0.0,None,0
Plank,60.0,60.0,sec,0.0,0.0,None,0
Russian Twists,20.0,20.0,reps,0.0,0.0,None,0
Russian Twists,20.0,20.0,reps,0.0,0.0,None,0
Russian Twists,20.0,20.0,reps,0.0,0.0,None,0
Leg Raises,15.0,15.0,reps,0.0,0.0,None,0
Leg Raises,15.0,15.0,reps,0.0,0.0,None,0
Leg Raises,15.0,15.0,reps,0.0,0.0,None,0
Tuesday:
General Climbing Warm-up,15.0,15.0,min,0.0,0.0,None,0
Bouldering (V4 Problem 1),1.0,1.0,attempt,8.0,0.0,RPE,0
Bouldering (V4 Problem 1),1.0,1.0,attempt,8.0,0.0,RPE,0
Bouldering (V5 Problem 2),1.0,1.0,attempt,9.0,0.0,RPE,0
Bouldering (V5 Problem 2),1.0,1.0,attempt,9.0,0.0,RPE,0
Bouldering (V5 Problem 3),1.0,1.0,attempt,9.0,0.0,RPE,0
Bouldering (V5 Problem 3),1.0,1.0,attempt,9.0,0.0,RPE,0
Bouldering (V6 Problem 4),1.0,1.0,attempt,10.0,0.0,RPE,0
Bouldering (V6 Problem 4),1.0,1.0,attempt,10.0,0.0,RPE,0
Bouldering (V4 Problem 5),1.0,1.0,attempt,8.0,0.0,RPE,0
Bouldering (V4 Problem 5),1.0,1.0,attempt,8.0,0.0,RPE,0
Bouldering (V5 Problem 6),1.0,1.0,attempt,9.0,0.0,RPE,0
Bouldering (V5 Problem 6),1.0,1.0,attempt,9.0,0.0,RPE,0
Push-ups,12.0,12.0,reps,0.0,0.0,bodyweight,0
Push-ups,12.0,12.0,reps,0.0,0.0,bodyweight,0
Push-ups,12.0,12.0,reps,0.0,0.0,bodyweight,0
Dips,10.0,10.0,reps,0.0,0.0,bodyweight,0
Dips,10.0,10.0,reps,0.0,0.0,bodyweight,0
Dips,10.0,10.0,reps,0.0,0.0,bodyweight,0
Dumbbell Overhead Press,10.0,10.0,reps,25.0,0.0,lbs,0
Dumbbell Overhead Press,10.0,10.0,reps,25.0,0.0,lbs,0
Dumbbell Overhead Press,10.0,10.0,reps,25.0,0.0,lbs,0
Thursday:
Easy Run,10.0,10.0,min,140.0,0.0,bpm,0
Dynamic Stretching,5.0,5.0,min,0.0,0.0,None,0
Endurance Run,60.0,60.0,min,155.0,0.0,bpm,0
Cool Down Run,5.0,5.0,min,130.0,0.0,bpm,0
Goblet Squat,10.0,10.0,reps,40.0,0.0,lbs,0
Goblet Squat,10.0,10.0,reps,40.0,0.0,lbs,0
Goblet Squat,10.0,10.0,reps,40.0,0.0,lbs,0
Walking Lunges,12.0,12.0,reps_per_leg,0.0,0.0,bodyweight,0
Walking Lunges,12.0,12.0,reps_per_leg,0.0,0.0,bodyweight,0
Walking Lunges,12.0,12.0,reps_per_leg,0.0,0.0,bodyweight,0
Calf Raises,20.0,20.0,reps,0.0,0.0,bodyweight,0
Calf Raises,20.0,20.0,reps,0.0,0.0,bodyweight,0
Calf Raises,20.0,20.0,reps,0.0,0.0,bodyweight,0
Box Jumps,8.0,8.0,reps,0.0,0.0,None,0
Box Jumps,8.0,8.0,reps,0.0,0.0,None,0
Box Jumps,8.0,8.0,reps,0.0,0.0,None,0
Saturday:
General Climbing Warm-up,15.0,15.0,min,0.0,0.0,None,0
Traverse Training,30.0,30.0,min,7.0,0.0,RPE,0
Route Climbing (5.10c),1.0,1.0,route_attempt,8.0,0.0,RPE,0
Route Climbing (5.10c),1.0,1.0,route_attempt,8.0,0.0,RPE,0
Route Climbing (5.11a),1.0,1.0,route_attempt,9.0,0.0,RPE,0
Route Climbing (5.11a),1.0,1.0,route_attempt,9.0,0.0,RPE,0
Route Climbing (5.11b),1.0,1.0,route_attempt,10.0,0.0,RPE,0
Route Climbing (5.11b),1.0,1.0,route_attempt,10.0,0.0,RPE,0
Fingerboard (Open Hand),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Open Hand),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Open Hand),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Crimp),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Crimp),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Crimp),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Pocket),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Pocket),10.0,10.0,sec,0.0,0.0,bodyweight,0
Fingerboard (Pocket),10.0,10.0,sec,0.0,0.0,bodyweight,0
Weighted Pull-ups,8.0,8.0,reps,15.0,0.0,lbs,0
Weighted Pull-ups,8.0,8.0,reps,15.0,0.0,lbs,0
Weighted Pull-ups,8.0,8.0,reps,15.0,0.0,lbs,0
Dumbbell Rows,10.0,10.0,reps_per_arm,20.0,0.0,lbs,0
Dumbbell Rows,10.0,10.0,reps_per_arm,20.0,0.0,lbs,0
Dumbbell Rows,10.0,10.0,reps_per_arm,20.0,0.0,lbs,0
"""
    days = parse_workouts(day_g)
    print(days)
    import json

    with open("week_1.json", "w+") as f:
        json.dump([d.model_dump() for d in days], f, indent=2)

