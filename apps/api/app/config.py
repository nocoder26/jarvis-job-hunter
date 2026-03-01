from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_key: str

    # AI
    gemini_api_key: str

    # Job Sources
    theirstack_api_key: str = ""
    serpapi_api_key: str = ""

    # Contact Discovery
    apollo_api_key: str = ""
    zerobounce_api_key: str = ""
    proxycurl_api_key: str = ""

    # App settings
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
