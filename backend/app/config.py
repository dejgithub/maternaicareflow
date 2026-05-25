from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017/maternaicareflow"
    database_name: str = "maternaicareflow"
    secret_key: str = "dev-secret-key"
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@maternaicareflow.com"
    uipath_maestro_api_url: Optional[str] = None
    uipath_maestro_api_key: Optional[str] = None
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
