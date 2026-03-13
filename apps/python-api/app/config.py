from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://drov-elektrik.vercel.app",
    ]
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    STORAGE_BUCKET_DRAWINGS: str = "drawings"
    STORAGE_BUCKET_LABELS: str = "labels"

    class Config:
        env_file = ".env"


settings = Settings()
