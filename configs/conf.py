from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_name: str
    database_username: str
    database_password: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    reset_password: str
    port: int
    host: str

    class Config:
        env_file = ".env"

settings = Settings()
