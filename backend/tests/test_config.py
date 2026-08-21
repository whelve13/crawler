"""Tests for configuration that do NOT require PostgreSQL."""
import os
from unittest.mock import patch


def test_database_url_takes_precedence():
    """
    Verify that when DATABASE_URL is set in the environment,
    it takes precedence over the individual POSTGRES_* variables.
    """
    custom_url = "postgresql+asyncpg://custom_user:custom_pass@custom_host/custom_db"
    env_overrides = {
        "DATABASE_URL": custom_url,
        "POSTGRES_SERVER": "should_be_ignored",
        "POSTGRES_USER": "should_be_ignored",
        "POSTGRES_PASSWORD": "should_be_ignored",
        "POSTGRES_DB": "should_be_ignored",
    }
    with patch.dict(os.environ, env_overrides, clear=False):
        # Import fresh settings — pydantic_settings reads env vars at construction time
        from app.core.config import Settings
        s = Settings()
        assert s.SQLALCHEMY_DATABASE_URI == custom_url


def test_individual_postgres_vars_compose_url():
    """
    Verify that when DATABASE_URL is NOT set, the URL is composed
    from the individual POSTGRES_* variables.
    """
    env_overrides = {
        "POSTGRES_SERVER": "myhost",
        "POSTGRES_USER": "myuser",
        "POSTGRES_PASSWORD": "mypass",
        "POSTGRES_DB": "mydb",
    }
    # Ensure DATABASE_URL is not set
    env_clean = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    env_clean.update(env_overrides)
    with patch.dict(os.environ, env_clean, clear=True):
        from app.core.config import Settings
        s = Settings()
        assert s.SQLALCHEMY_DATABASE_URI == "postgresql+asyncpg://myuser:mypass@myhost/mydb"


def test_default_settings_are_safe():
    """
    Verify defaults exist and the application doesn't crash on import.
    """
    from app.core.config import Settings
    s = Settings()
    assert s.PROJECT_NAME == "Website Auditor"
    assert s.MAX_CONCURRENCY > 0
    assert s.MAX_FILE_SIZE_BYTES > 0
    assert s.DB_POOL_SIZE > 0
