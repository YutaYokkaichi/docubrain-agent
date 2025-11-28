from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuBrain-Agent"
    API_V1_STR: str = "/api/v1"
    
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Qdrant Settings
    QDRANT_HOST: str 
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()