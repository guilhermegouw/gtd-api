from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    DATABASE_URL: str = (
        "postgresql+asyncpg://gtd_user:gtd_password@localhost:5432/gtd"
    )

    class Config:
        env_file = ".env"


settings = Settings()
