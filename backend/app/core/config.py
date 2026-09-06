import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "job-tracker-prod")
    FIRESTORE_DATABASE: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    PUBSUB_NUDGE_TOPIC: str = os.getenv("PUBSUB_NUDGE_TOPIC", "nudge-events")
    SENDGRID_SECRET_NAME: str = os.getenv("SENDGRID_SECRET_NAME", "sendgrid-api-key")
    GEMINI_API_KEY_SECRET_NAME: str = os.getenv("GEMINI_API_KEY_SECRET_NAME", "gemini-api-key")
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 10
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
