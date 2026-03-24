from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "NLP Finance NER Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    SPACY_MODEL: str = "en_core_web_sm"

    class Config:
        env_file = ".env"


settings = Settings()
