from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Backend selection: "mock" needs no credentials and is used for local dev/tests.
    # "openai" is the real fallback standing in for NVIDIA NeMo/NIM until those are wired in.
    asr_backend: str = "mock"
    nlp_backend: str = "mock"

    openai_api_key: str | None = None
    asr_model: str = "whisper-1"
    nlp_model: str = "gpt-4o-mini"

    postgres_dsn: str = "postgresql+psycopg2://clinicalvoice:clinicalvoice@localhost:5432/clinicalvoice"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
