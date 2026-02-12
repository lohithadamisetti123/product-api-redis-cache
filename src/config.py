from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    API_PORT: int = 8080
    DATABASE_URL: AnyUrl = "postgresql+psycopg2://postgres:postgres@db:5432/productdb"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    CACHE_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
