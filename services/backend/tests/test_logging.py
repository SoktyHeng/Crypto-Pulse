import json
import logging

from app.core.logging import REDACTED, JsonFormatter
from app.core.request_context import set_request_id


def _record(msg: str, **extra: object) -> logging.LogRecord:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, msg, None, None)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_formats_one_json_object_with_utc_timestamp() -> None:
    set_request_id("req-1")
    try:
        line = JsonFormatter("api").format(_record("hello", symbol="BTCUSDT", lag_ms=12))
    finally:
        set_request_id(None)
    payload = json.loads(line)
    assert payload["message"] == "hello"
    assert payload["component"] == "api"
    assert payload["request_id"] == "req-1"
    assert payload["symbol"] == "BTCUSDT"
    assert payload["lag_ms"] == 12
    assert payload["ts"].endswith("+00:00")


def test_redacts_secret_context_keys() -> None:
    record = _record(
        "x",
        context={"database_url": "postgresql://u:pw@h/d", "api_key": "k", "rows": 3},
    )
    payload = json.loads(JsonFormatter("api").format(record))
    assert payload["database_url"] == REDACTED
    assert payload["api_key"] == REDACTED
    assert payload["rows"] == 3
