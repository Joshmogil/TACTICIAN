# --- Configuration ---
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_a_env_file"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GOOGLE_CLIENT_ID: str = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
    GEMINI_API_KEY: str = 'top_secret-api_key'
    TEST_USER_PASS: str = 'super-duper-secret'


    class Config:
        env_file = ".env"

settings = Settings()