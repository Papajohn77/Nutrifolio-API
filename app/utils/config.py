from pydantic import BaseSettings


class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_name: str
    database_user: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 60


settings = Settings()
