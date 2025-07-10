from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from contextlib import asynccontextmanager
from pydantic import BaseModel

from app.workout import WorkoutDay
from app.auth import (
    create_access_token,
    get_current_user,
    verify_google_token,
    Token,
)
from app.user import User, test_users  # Assuming you have a user model
from app.routes.user import router as user_router
from app.routes.workout import router as workout_router

from tortoise import Tortoise

TEST_USER = test_users['josh']


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    # Startup: Initialize Tortoise ORM
    print("Connecting to the database...")
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['app.db.models']}
    )
    # Generate the database schemas
    await Tortoise.generate_schemas()
    print("Database connection established.")
    
    yield  # The application is now running
    
    # Shutdown: Close Tortoise ORM connections
    print("Closing database connections...")
    await Tortoise.close_connections()
    print("Database connections closed.")

# Pass the lifespan handler to the FastAPI app
app = FastAPI(lifespan=lifespan)

# Register API routers
app.include_router(user_router)
app.include_router(workout_router)

class ProviderToken(BaseModel):
    token: str

@app.post("/auth/login/google", response_model=Token)
async def login_with_google(provider_token: ProviderToken):
    idinfo = verify_google_token(provider_token.token)
    if not idinfo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    
    user_email = idinfo.get("email")
    # Here, you would find or create the user in your database
    # user = get_or_create_user(email=user_email, name=idinfo.get("name"))

    # Create an access token for your app
    access_token = create_access_token(data={"sub": user_email})
    return {"access_token": access_token, "token_type": "bearer"}

# Example of a protected endpoint
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    # In a real app, you'd return the full user object from the DB
    # For now, we just return the email from the token
    return {"name": "Dummy User", "email": current_user.email}

@app.get("/week/my", response_model=List[WorkoutDay])
def get_my_week(current_user: User = Depends(get_current_user)):
    # You can now use current_user.email to fetch data specific to that user
    # For now, returning sample data
    return [
        WorkoutDay(
            day="Monday",
            workout=[...] # workout data
        )
    ]