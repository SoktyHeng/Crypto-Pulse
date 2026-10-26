import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.domain.enums import CandleInterval, HorizonMinutes, SupportedSymbol
from tests.conftest import make_settings


def test_defaults_match_mvp_scope() -> None:
    settings = Settings()
    assert settings.supported_symbols == [
        SupportedSymbol.BTCUSDT,
        SupportedSymbol.ETHUSDT,
        SupportedSymbol.SOLUSDT,
    ]
    assert settings.prediction_horizons_minutes == [15, 30, 60, 240]
    assert settings.primary_candle_interval is CandleInterval.M1
    assert settings.max_candle_staleness_seconds == 120
    assert settings.enable_demo_mode is False
    assert settings.binance_rest_base == "https://data-api.binance.vision"


def test_parses_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPPORTED_SYMBOLS", " btcusdt , ETHUSDT ")
    monkeypatch.setenv("PREDICTION_HORIZONS_MINUTES", "15,60")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    settings = Settings()
    assert settings.supported_symbols == [SupportedSymbol.BTCUSDT, SupportedSymbol.ETHUSDT]
    assert settings.prediction_horizons_minutes == [HorizonMinutes.M15, HorizonMinutes.H1]
    assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("supported_symbols", "BTCUSDT,DOGEUSDT"),  # not whitelisted
        ("supported_symbols", "BTCUSD"),  # different quote market must not be substituted
        ("supported_symbols", ""),
        ("supported_symbols", "BTCUSDT,BTCUSDT"),
        ("prediction_horizons_minutes", "15,45"),
        ("prediction_horizons_minutes", "5,15"),  # research-gated
        ("cors_origins", "*"),
        ("primary_candle_interval", "2m"),
        ("database_url", "mysql://user@host/db"),
        ("app_env", "staging"),
    ],
)
def test_rejects_invalid_values(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        make_settings(**{field: value})


def test_database_url_is_not_exposed_in_repr() -> None:
    settings = make_settings(database_url="postgresql+psycopg://u:topsecret@db:5432/x")
    assert "topsecret" not in repr(settings)
    assert "topsecret" not in str(settings.model_dump())
