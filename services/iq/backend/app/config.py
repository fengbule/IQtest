from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:////app/data/iq.db"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    admin_username: str = "admin"
    admin_password: str
    public_base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
