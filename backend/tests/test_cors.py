from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def preflight(origin: str):
    """Simulate the browser's permission check before a cross-site request."""
    return client.options(
        "/api/machines",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )


def test_allowed_origin_gets_cors_header():
    r = preflight("http://localhost:5173")
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_unknown_origin_is_blocked():
    r = preflight("https://evil.example")
    assert "access-control-allow-origin" not in r.headers