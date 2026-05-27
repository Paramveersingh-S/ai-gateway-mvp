from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gateway_api_key: str = "my-secret-gateway-key"
    groq_api_key: str = ""
    agent_model: str = "llama3-8b-8192"
    upstream_model: str = "llama3-8b-8192"
    triage_mode: str = "rule"
    database_url: str = "sqlite+aiosqlite:///./gateway.db"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()