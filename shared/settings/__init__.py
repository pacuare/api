from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url_base: str
    database_data: str = "data"
    database_url: str
    resend_api_key: str
    fernet_key: str
    cookie_domain: str = ".pacuare.dev"
    sprites_token: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get() -> Settings:
    return Settings()  # ty:ignore[missing-argument]
