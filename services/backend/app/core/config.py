"""Typed application settings loaded from environment variables (see `.env.example`)."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.domain.enums import CandleInterval, HorizonMinutes, SupportedSymbol

AppEnv = Literal["development", "test", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _split_csv(value: object) -> object:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore", frozen=True)

    app_env: AppEnv = "development"
    log_level: LogLevel = "INFO"

    # Wrapped in SecretStr so the password never appears in reprs or logs.
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://cryptopulse:local_change_me@localhost:5432/cryptopulse"
    )
    database_connect_timeout_seconds: int = Field(default=3, ge=1, le=30)

    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    binance_rest_base: str = "https://data-api.binance.vision"
    binance_ws_base: str = "wss://data-stream.binance.vision:443"
    supported_symbols: Annotated[list[SupportedSymbol], NoDecode] = list(SupportedSymbol)
    primary_candle_interval: CandleInterval = CandleInterval.M1
    prediction_horizons_minutes: Annotated[list[HorizonMinutes], NoDecode] = [
        HorizonMinutes.M15,
        HorizonMinutes.M30,
        HorizonMinutes.H1,
        HorizonMinutes.H4,
    ]
    max_candle_staleness_seconds: int = Field(default=120, ge=1)

    model_artifact_dir: str = "/app/artifacts/models"
    enable_demo_mode: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_origins(cls, value: object) -> object:
        return _split_csv(value)

    @field_validator("supported_symbols", mode="before")
    @classmethod
    def _parse_symbols(cls, value: object) -> object:
        parsed = _split_csv(value)
        if isinstance(parsed, list):
            return [str(item).upper() for item in parsed]
        return parsed

    @field_validator("prediction_horizons_minutes", mode="before")
    @classmethod
    def _parse_horizons(cls, value: object) -> object:
        parsed = _split_csv(value)
        if isinstance(parsed, list):
            return [int(item) for item in parsed]
        return parsed

    @field_validator("supported_symbols", "prediction_horizons_minutes", "cors_origins")
    @classmethod
    def _non_empty_unique(cls, value: list[object]) -> list[object]:
        if not value:
            raise ValueError("must contain at least one value")
        if len(set(value)) != len(value):
            raise ValueError("must not contain duplicates")
        return value

    @field_validator("cors_origins")
    @classmethod
    def _no_wildcard_origin(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("wildcard CORS origin is not allowed; list explicit origins")
        return value

    @field_validator("prediction_horizons_minutes")
    @classmethod
    def _public_horizons_only(cls, value: list[HorizonMinutes]) -> list[HorizonMinutes]:
        if HorizonMinutes.M5 in value:
            raise ValueError("5m horizon is research-gated and cannot be enabled in the MVP")
        return value

    @field_validator("database_url")
    @classmethod
    def _postgres_url(cls, value: SecretStr) -> SecretStr:
        PostgresDsn(value.get_secret_value())
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
