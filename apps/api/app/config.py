import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_env: str = os.getenv("API_ENV", "development")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "")

    api_local_debug: bool = os.getenv("API_LOCAL_DEBUG", "").lower() in {"1", "true", "yes"}
    api_local_debug_user_id: str = os.getenv("API_LOCAL_DEBUG_USER_ID", "local-debug-user")

    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    supabase_project_ref: str = os.getenv("SUPABASE_PROJECT_REF", "")
    supabase_jwt_audience: str = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")


settings = Settings()
