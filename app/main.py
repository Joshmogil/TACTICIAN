from fastapi import FastAPI

from app.api import router
from workout import load_workout_data


app = FastAPI()

# Preload the sample workout CSV files for a default user
load_workout_data(user_id="Josh")

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
