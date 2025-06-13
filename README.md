# Fitness Tracking API

This repository contains a small FastAPI application for tracking workouts and estimating recovery.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the API

The API is defined in `app.main`. When the server starts it loads all CSV files in the `_Workouts/` directory for a default user named **Josh**. Exercises are populated from the YAML files in `exercises/`.

Start the server with:

```bash
uvicorn app.main:app --reload
```

Once running, open <http://localhost:8000/docs> to explore the endpoints.

## Loading Exercises Manually

You can inspect the exercise library by running:

```bash
python load_exercises.py
```

## Tests

Run the unit tests with:

```bash
pytest
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── main.py
│   ├── models.py
│   ├── recommendation.py
│   └── recovery.py
├── core.py
├── exercises/           # YAML exercise definitions
├── _Workouts/           # sample workout CSVs
├── workout.py
├── load_exercises.py
├── requirements.txt
└── tests/
```
