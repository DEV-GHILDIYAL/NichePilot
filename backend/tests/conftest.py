import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app.config import Settings, get_settings
from app.main import create_app


@pytest.fixture(scope="session")
def database_url():
    url = Settings().test_database_url
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")
    if not url.split("?", 1)[0].rsplit("/", 1)[-1].endswith("_test"):
        pytest.fail("TEST_DATABASE_URL must target a database ending in _test")
    os.environ["DATABASE_URL"] = url
    get_settings.cache_clear()
    config = Config("backend/alembic.ini")
    command.upgrade(config, "head")
    return url


@pytest.fixture
def client(database_url):
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE account_change_events, niche_dna_revisions, accounts CASCADE")
        )
    engine.dispose()
    settings = Settings(
        app_env="test", database_url=database_url, admin_api_token="test-admin-token"
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def auth():
    return {"Authorization": "Bearer test-admin-token"}


@pytest.fixture
def account_payload():
    return {
        "display_name": "Office Comedy",
        "platform": "instagram",
        "platform_handle": "office.comedy",
        "niche_dna": {
            "niche_name": "Indian relatable comedy",
            "niche_description": "Everyday situations presented as short comedy.",
            "target_audience": "Indian young adults",
            "language": "hi-IN",
            "tone": "Warm and playful",
            "content_pillars": [
                {"name": "Office life", "description": "Workplace situations"},
                {"name": "Indian parents", "description": "Family observations"},
            ],
            "forbidden_topics": ["Politics"],
            "trend_transformation_guidance": "Only use trends through a relatable comedy scenario.",
            "change_note": "Initial niche",
        },
    }
