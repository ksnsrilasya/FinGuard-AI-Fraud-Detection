"""
backend/config.py

Centralized application configuration, loaded from environment variables
(.env file). Avoids hardcoded paths/secrets scattered across modules.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; falls back to real env vars / defaults

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings:
    """Lightweight settings object, populated from environment variables
    (loaded from .env if python-dotenv is installed) with sane defaults.
    Avoids a hard dependency on pydantic-settings so the app still runs
    in minimal environments."""

    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "FinGuard")
        self.app_env = os.getenv("APP_ENV", "development")
        self.debug = os.getenv("DEBUG", "True").lower() == "true"

        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))

        self.database_path = os.getenv(
            "DATABASE_PATH", os.path.join(BASE_DIR, "backend", "finguard.db")
        )
        self.model_dir = os.getenv(
            "MODEL_DIR", os.path.join(BASE_DIR, "models", "artifacts")
        )

        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv(
            "LOG_FILE", os.path.join(BASE_DIR, "logs", "finguard.log")
        )

        self.secret_key = os.getenv("SECRET_KEY", "change-this-in-production")


settings = Settings()
