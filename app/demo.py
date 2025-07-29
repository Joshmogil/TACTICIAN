import argparse
import json
from app.ai.first_week import generate_raw_week, parse_workouts
from app.ai.progress_week import progress_day, progress_week
from app.workout import WorkoutDay, WorkoutWeek
from app.user import UserInfo, Interest, Range, UserFeedback
import pandas as pd

josh = UserInfo(
    interests=[
            Interest(name="cardio", skill="Novice"),
            Interest(
                name="lifting weights",
                skill="Intermediate"
                ),
            Interest(
                name="functional strength training",
                skill="Intermediate"
                ),
            Interest(
                name="stretching",
                skill="Intermediate"
                )
    ],
    desired_workouts_per_week=Range(start=4, end=5),
    favorite_exercises=[
        "jogging",
        "dumbbell benchpress",
        "curl and press",
        "dumbbell lunge",
        "stair climber",
        "pull ups",
        "lat pulldown"
    ],
    age="27",
    activity_level="Active",
    gender="male",
    name="Josh"
)

josh_feedback=UserFeedback(
    biceps = "Just right",
    triceps = "Just right",
    forearms = "Just right",
    hands = "Just right",
    rear_deltoids = "Not enough",
    middle_deltoids = "Not enough",
    front_deltoids = "Just right",
    upper_chest = "Just right",
    chest = "Just right",
    traps = "Not enough",
    upper_back = "Not enough",
    lats = "Not enough",
    abs = "Just right",
    obliques = "Just right",
    lower_back = "Just right",
    glutes = "Just right",
    hamstrings = "Just right",
    quads = "Just right",
    calves = "Just right",

    interest_reports={
        "lifting weights":[
            "More volume",
        ],
        "stretching":[
            "More often",
        ],
        "functional strength training":[
            "More volume",
        ],
        "cardio":[
            "More exercise variety",
            "More often",
        ]
    }

)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["base", "next"], required=True, help="Mode: base or next")
    parser.add_argument("--week-num", type=int, default=0, help="Week number for next mode")
    parser.add_argument("--convert-to-csv", action="store_true", help="Convert output to CSV")
    args = parser.parse_args()

    if args.mode == "base":
        raw_week = generate_raw_week(josh)
        days = parse_workouts(raw_week)
        with open("week_1.json", "w") as f:
            json.dump([d.model_dump() for d in days], f, indent=2)
        if args.convert_to_csv:
            for i, d in enumerate(days):
                df = d.workout_df()
                df.to_csv(f"week_1_day_{i+1}_{d.day}.csv", index=False)

    elif args.mode == "next":
        week_num = args.week_num
        with open(f"week_{week_num}.json", "r") as f:
            week = json.load(f)
        week = [WorkoutDay(**obj) for obj in week]
        week = WorkoutWeek(content=week)
        
        wk = progress_week(josh, week,josh_feedback, week_goal="Increase")
        print(wk)
        parsed_workouts = parse_workouts(wk)
        #for workout in week:
        #    w = progress_day(user=josh, workout=workout, week_goal="Increase")
        #    print(w)
        #    p = parse_workouts(w)
        #    parsed_workouts.append(p[0])

        with open(f"week_{week_num+1}.json", "w") as f:
            json.dump([d.model_dump() for d in parsed_workouts], f, indent=2)
        if args.convert_to_csv:
            for i, d in enumerate(parsed_workouts):
                df = d.workout_df()
                df.to_csv(f"week_{week_num+1}_day_{i+1}_{d.day}.csv", index=False)

if __name__ == "__main__":
    import json
    with open("josh.json", "w") as f:
        json.dump(josh.model_dump(), f, indent=2)
    
    with open("josh_feedback.json", "w") as f:
        json.dump(josh_feedback.model_dump(), f, indent=2)

    main()