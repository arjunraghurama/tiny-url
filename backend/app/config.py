from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://tinyurl:tinyurl_secret@postgres:5432/tinyurl"
    VALKEY_URL: str = "valkey://valkey:6379/0"
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 7

    # Keycloak
    KEYCLOAK_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "myrealm"
    KEYCLOAK_CLIENT_ID: str = "react-client"

    class Config:
        env_file = ".env"


settings = Settings()
