import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_env: str = os.getenv("API_ENV", "development")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "")

    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    supabase_project_ref: str = os.getenv("SUPABASE_PROJECT_REF", "")


settings = Settings()
