import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import os
import dotenv


dotenv.load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 1 days = 1 day
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    # SERVER_NAME: str
    SERVER_HOST:str = "localhost"# AnyHttpUrl
    # # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: 'z"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    #
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    #
    PROJECT_NAME: str

    #
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "email-templates/"
    EMAILS_ENABLED: bool = True
    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            os.getenv("SMTP_HOST")#values.get("SMTP_HOST")
            and os.getenv("SMTP_PORT")#and values.get("SMTP_PORT")  # noqa
            and os.getenv("EMAILS_FROM_EMAIL")#values.get("EMAILS_FROM_EMAIL")  # noqa
        )

    EMAIL_TEST_USER: EmailStr = "stiveckamash@gmail.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False


    #
    class Config:
        case_sensitive = True
        env_file = './.env'


settings = Settings()
