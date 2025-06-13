# Fitness Tracking and Workout Planning Application

A FastAPI-based application for tracking fitness activities, exercises, and workout progress. The application includes features for load balancing and progress tracking.

## Features

- Activity management (weightlifting, cardio, etc.)
- Exercise tracking with multiple measurement types
- Workout planning with load balancing
- Progress tracking over time
- Recovery monitoring
- RESTful API endpoints

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the application:
```bash
python run.py
```

The server will start at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Creating an Activity

```python
import requests

activity = {
    "name": "Powerlifting",
    "type": "weightlifting",
    "style": "powerlifting",
    "experience_level": "intermediate",
    "peak_performance": 315.0,
    "favorite_exercises": ["bench_press", "squat", "deadlift"],
    "mix_new_exercises": True
}

response = requests.post("http://localhost:8000/api/v1/activities/", json=activity)
```

### Creating an Exercise

```python
exercise = {
    "name": "Bench Press",
    "activity_id": 1,
    "description": "Classic chest exercise",
    "measurement_types": ["weight", "reps"],
    "primary_muscle_groups": ["chest", "triceps"],
    "secondary_muscle_groups": ["shoulders"],
    "intensity_factor": 1.2,
    "recovery_days": 3
}

response = requests.post("http://localhost:8000/api/v1/exercises/", json=exercise)
```

### Creating a Workout

```python
workout = {
    "activity_id": 1,
    "duration": 90,
    "intensity": 8.5,
    "notes": "Upper body focus day",
    "exercises": [
        {
            "exercise_id": 1,
            "sets": 4,
            "measurements": {
                "weight": 225,
                "reps": 8
            },
            "rest_time": 120,
            "order": 1,
            "notes": "Focus on form"
        }
    ]
}

response = requests.post("http://localhost:8000/api/v1/workouts/", json=workout)
```

## Database Migrations

The application uses Alembic for database migrations. To create a new migration:

1. Make changes to the models in `app/models.py`
2. Generate a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```
3. Apply the migration:
```bash
alembic upgrade head
```

## Project Structure

```
.
├── alembic/              # Database migrations
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # CRUD operations
│   ├── routes.py        # API routes
│   └── services.py      # Business logic
├── requirements.txt     # Project dependencies
├── run.py              # Application entry point
└── init_db.py          # Database initialization
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 
## Loading Built-in Exercises

Use `load_exercises.py` to read the predefined exercise YAML files.
The script relies on PyYAML, so make sure the dependencies are installed:

```bash
python load_exercises.py
```

This will print the number of exercises parsed from the `exercises/` folder.

