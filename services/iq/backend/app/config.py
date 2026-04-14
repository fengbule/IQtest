from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:////app/data/iq.db"
    jwt_secret: str = "change_this_jwt_secret_to_a_long_random_string"
    jwt_algorithm: str = "HS256"
    admin_username: str = "admin"
    admin_password: str = "ChangeThisAdminPassword123!"
    public_base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
