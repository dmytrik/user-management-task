from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_name: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
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
        elif self.environment == "docker":
            return (
                f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
                f"@{self.db_host}:{self.postgres_port}/{self.postgres_name}"
            )
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.db_host}:{self.postgres_port}/{self.postgres_name}"
        )


settings = Settings()
