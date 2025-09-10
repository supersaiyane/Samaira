import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER", "finops")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "finops123")
    DB_NAME: str = os.getenv("DB_NAME", "finopsdb")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()
