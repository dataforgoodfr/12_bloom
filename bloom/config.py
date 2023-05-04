from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url: str = Field(
        "postgresql://bloom_user:bloom@postgres_bloom:5432/bloom_db",
        env="DATABASE_URL",
    )
    srid: int = 4236


settings = Settings()
