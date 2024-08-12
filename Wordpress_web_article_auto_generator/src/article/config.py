from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for API keys."""

    SERPER_API_KEY: str = Field(..., env="SERPER_API_KEY")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


config = Settings()