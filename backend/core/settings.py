from pydantic_settings import BaseSettings, SettingsConfigDict

"""
Настройки. Берутся из переменных окружения, с помощью pydantic
"""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "e-comet"

    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_pass: str

    gh_auth_token: str


settings = Settings()
