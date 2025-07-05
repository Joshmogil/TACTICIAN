import re
from typing import List
from app.workout import WorkoutDay, WorkDone

def parse_workouts(raw_text: str) -> List[WorkoutDay]:
    days: List[WorkoutDay] = []
    week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    # Regex to match each day and its block, even if the header is on the same line as the first workout
    pattern = r'(' + '|'.join(day + ':' for day in week_days) + r')'
    # Find all matches with their positions
    matches = list(re.finditer(pattern, raw_text))
    for idx, match in enumerate(matches):
        day_header = match.group(0)[:-1]  # Remove the colon
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
        workouts_block = raw_text[start:end].strip()
        # Split lines, but also handle the case where the first workout is on the same line as the header
        lines = []
        if '\n' in workouts_block:
            lines = [line.strip() for line in workouts_block.splitlines() if line.strip()]
        else:
            # All workouts are on one line, comma-separated
            lines = [l.strip() for l in workouts_block.split(',') if l.strip()]
            # Recombine every 8 fields into a workout line
            lines = [','.join(lines[i:i+8]) for i in range(0, len(lines), 8)]
        workout_objs = []
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 8:
                continue  # skip malformed lines
            try:
                workout_objs.append(
                    WorkDone(
                        exercise=parts[0],
                        amount=float(parts[1]),
                        actual_amount=float(parts[2]),
                        amount_unit=parts[3],
                        intensity=float(parts[4]),
                        actual_intensity=float(parts[5]),
                        intensity_unit=parts[6] if parts[6] else "",
                        perceived_exertion=parts[7] if parts[7] else None
                    )
                )
            except Exception as e:
                print(f"Error parsing line: {line}\n{e}")
        days.append(WorkoutDay(day=day_header, workout=workout_objs))
    return days

if __name__ == "__main__":
    day="""
Tuesday: Dynamic Stretches,5.0,5.0,min,0.0,0.0,,0
Jogging,35.0,0.0,min,130.0,0.0,bpm,0
Russian Twist,15.0,0.0,reps,12.5,0.0,lbs,0
Russian Twist,15.0,0.0,reps,12.5,0.0,lbs,0
Russian Twist,15.0,0.0,reps,12.5,0.0,lbs,0
Leg Raise,18.0,0.0,reps,0.0,0.0,,0
Leg Raise,18.0,0.0,reps,0.0,0.0,,0
Leg Raise,18.0,0.0,reps,0.0,0.0,,0
Side Plank,35.0,0.0,seconds,0.0,0.0,,0
Side Plank,35.0,0.0,seconds,0.0,0.0,,0
Side Plank,35.0,0.0,seconds,0.0,0.0,,0
Light Walk,5.0,5.0,min,0.0,0.0,bpm,0
"""
    p =parse_workouts(day)
    print(p)