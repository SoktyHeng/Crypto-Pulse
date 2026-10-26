from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_reports_liveness_in_utc(client: TestClient) -> None:
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "cryptopulse-api"
    assert body["environment"] == "test"
    parsed = datetime.fromisoformat(body["time"])
    assert parsed.utcoffset() == UTC.utcoffset(None)


def test_every_response_has_a_request_id(client: TestClient) -> None:
    response = client.get("/api/v1/system/health")
    assert len(response.headers["X-Request-ID"]) == 32


def test_safe_incoming_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/api/v1/system/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_unsafe_incoming_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/api/v1/system/health", headers={"X-Request-ID": "bad id\nInjected: 1"})
    assert response.headers["X-Request-ID"] != "bad id\nInjected: 1"


def test_readiness_without_database_is_503_and_sanitized(client: TestClient) -> None:
    response = client.get("/api/v1/system/readiness")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    components = {c["name"]: c for c in body["components"]}
    assert components["database"]["code"] == "DATABASE_UNAVAILABLE"
    # Feed and model are reported honestly as unavailable, never as working.
    assert components["market_feed"]["code"] == "DATA_UNAVAILABLE"
    assert components["model"]["code"] == "MODEL_UNAVAILABLE"
    raw = response.text
    for leaked in ("s3cret-pw", "127.0.0.1", "psycopg", "Traceback", "/app/"):
        assert leaked not in raw


def test_unknown_route_uses_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_write_methods_are_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/system/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_validation_errors_are_400_envelopes(settings: Settings) -> None:
    app = create_app(settings)
    router = APIRouter()

    @router.get("/probe")
    def probe(limit: int) -> dict[str, int]:
        return {"limit": limit}

    app.include_router(router)
    response = TestClient(app).get("/probe", params={"limit": "many"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "INVALID_REQUEST"
    assert body["error"]["details"]["issues"][0]["loc"] == ["query", "limit"]


def test_unhandled_errors_do_not_leak_internals(settings: Settings) -> None:
    app = create_app(settings)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("/secret/path/model.pkl exploded")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "secret" not in response.text
    assert body["request_id"]


def test_cors_allows_only_configured_origins(client: TestClient) -> None:
    allowed = client.get("/api/v1/system/health", headers={"Origin": "http://localhost:3000"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    denied = client.get("/api/v1/system/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in denied.headers


def test_openapi_is_versioned(client: TestClient) -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert set(paths) == {"/api/v1/system/health", "/api/v1/system/readiness"}
