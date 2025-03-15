from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def db_host(self) -> str:
        if self.environment == "local":
            return "localhost"
        return "db"

    @property
    def database_url(self) -> str:
        if self.environment == "testing":
            return "sqlite:///:memory:"
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
