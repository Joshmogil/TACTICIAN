from fastapi import FastAPI

from app.api import router
from workout import load_user_history


app = FastAPI()

# Preload the sample workout CSV files for a default user and
# apply them to the in-memory state so recommendations work
load_user_history(user_id="Josh")

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
