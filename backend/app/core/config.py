from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Website Auditor"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "website_auditor"

    # Crawler Settings
    MAX_CONCURRENCY: int = 10
    DEFAULT_TIMEOUT: float = 10.0
    USER_AGENT: str = "WebsiteAuditorBot/1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
