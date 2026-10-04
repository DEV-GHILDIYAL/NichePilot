from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = ""
    test_database_url: str = ""
    admin_api_token: str = ""
    global_automation_enabled: bool = False
    publishing_enabled: bool = False
    dry_run: bool = True
    require_manual_approval: bool = True

    def validate_startup(self) -> None:
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is required")
        if self.app_env != "test" and len(self.admin_api_token) < 32:
            raise RuntimeError("ADMIN_API_TOKEN must contain at least 32 characters")
        if self.global_automation_enabled or self.publishing_enabled or not self.dry_run:
            raise RuntimeError("Phase 1 supports safe defaults only")


@lru_cache
def get_settings() -> Settings:
    return Settings()
