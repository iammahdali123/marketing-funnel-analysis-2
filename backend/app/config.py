from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://funnel:funnel@db:5432/funnel_db"
    app_name: str = "Marketing Funnel Analyzer"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
