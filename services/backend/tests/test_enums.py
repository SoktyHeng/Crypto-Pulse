from app.domain.enums import (
    CANONICAL_CLASS_ORDER,
    PUBLIC_MVP_HORIZONS,
    CandleInterval,
    ExchangeCode,
    FeedStatus,
    HorizonMinutes,
    PredictedClass,
    SupportedSymbol,
)


def test_symbols_are_binance_spot_usdt_only() -> None:
    assert [s.value for s in SupportedSymbol] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    assert all(s.value.endswith("USDT") for s in SupportedSymbol)
    assert [e.value for e in ExchangeCode] == ["BINANCE_SPOT"]


def test_canonical_class_order_is_fixed() -> None:
    assert CANONICAL_CLASS_ORDER == (
        PredictedClass.UP,
        PredictedClass.DOWN,
        PredictedClass.SIDEWAYS,
    )


def test_public_horizons_exclude_research_gated_5m() -> None:
    assert [int(h) for h in PUBLIC_MVP_HORIZONS] == [15, 30, 60, 240]
    assert HorizonMinutes.M5 not in PUBLIC_MVP_HORIZONS


def test_candle_interval_minutes() -> None:
    assert {i.value: i.minutes for i in CandleInterval} == {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
    }


def test_feed_statuses_match_contract() -> None:
    assert [s.value for s in FeedStatus] == [
        "CONNECTED",
        "RECONNECTING",
        "DEGRADED",
        "STALE",
        "OFFLINE",
    ]
