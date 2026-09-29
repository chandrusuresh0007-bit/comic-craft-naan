import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    """
    Application configuration.

    Values can be overridden through environment variables.
    """

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "PocketSmart AI",
    )

    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    HOST: str = os.getenv(
        "HOST",
        "127.0.0.1",
    )

    PORT: int = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )

    # -----------------------------------------------------
    # Security
    # -----------------------------------------------------

    SESSION_SECRET: str = os.getenv(
        "SESSION_SECRET",
        "change-this-session-secret",
    )

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "change-this-jwt-secret",
    )

    JWT_ALGORITHM: str = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_MINUTES",
            "120",
        )
    )

    COOKIE_SECURE: bool = (
        os.getenv(
            "COOKIE_SECURE",
            "false",
        ).lower()
        == "true"
    )

    # -----------------------------------------------------
    # Database
    # -----------------------------------------------------

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'pocketsmart.db'}",
    )

    # -----------------------------------------------------
    # Gemini
    # -----------------------------------------------------

    AI_PROVIDER: str = os.getenv(
        "AI_PROVIDER",
        "gemini",
    )

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-1.5-flash",
    )

    # -----------------------------------------------------
    # CORS
    # -----------------------------------------------------

    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://127.0.0.1:8000,http://localhost:8000",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
