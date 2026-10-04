import pytest
from pydantic import ValidationError

from app.accounts.schemas import AccountCreate
from app.config import Settings


def test_safe_defaults_reject_live_modes():
    settings = Settings(app_env="test", database_url="postgresql+psycopg://x:y@localhost/db")
    assert not settings.global_automation_enabled
    assert not settings.publishing_enabled
    assert settings.dry_run
    settings.publishing_enabled = True
    with pytest.raises(RuntimeError, match="safe defaults"):
        settings.validate_startup()
    with pytest.raises(RuntimeError, match="ADMIN_API_TOKEN"):
        Settings(
            app_env="development",
            database_url="postgresql+psycopg://x:y@localhost/db",
            admin_api_token="",
        ).validate_startup()


def test_niche_structure_rejects_blank_and_duplicate_values(account_payload):
    payload = account_payload.copy()
    niche = account_payload["niche_dna"].copy()
    niche["content_pillars"] = [{"name": "Office"}, {"name": " office "}]
    payload["niche_dna"] = niche
    with pytest.raises(ValidationError):
        AccountCreate.model_validate(payload)
    niche["content_pillars"] = [{"name": " "}]
    with pytest.raises(ValidationError):
        AccountCreate.model_validate(payload)
    niche["content_pillars"] = [{"name": "Office"}]
    niche["forbidden_topics"] = ["Politics", " politics "]
    with pytest.raises(ValidationError):
        AccountCreate.model_validate(payload)
