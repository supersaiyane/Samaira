import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER", "finops")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "finops123")
    DB_NAME: str = os.getenv("DB_NAME", "finopsdb")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    DB_DEBUG: bool = os.getenv("DB_DEBUG", "false").lower() == "true"

    USE_LLM_FALLBACK: bool = os.getenv("USE_LLM_FALLBACK", "false").lower() == "true"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")   # openai | anthropic | ollama
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()