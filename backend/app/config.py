from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"

    # Change this in .env for a real deployment.
    secret_key: str = "change-this-secret-key"

    # SQLite database
    database_url: str = "sqlite:///./pocketsmart.db"

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Frontend URL
    frontend_origin: str = "http://localhost:5173"

    # Uploaded images
    upload_dir: str = "./uploads"
    max_upload_mb: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()