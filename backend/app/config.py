from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tamtdb"
    db_user: str = "tamtuser"
    db_password: str = ""

    secret_key: str = "change-me"
    algorithm: str = "HS256"
    cookie_name: str = "access_token"
    cors_origins: str = ""

    debug: bool = False
    debug_aid: int = 1

    storage_path: str = "storage"
    max_upload_size: int = 10_485_760

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        if not self.cors_origins.strip():
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
