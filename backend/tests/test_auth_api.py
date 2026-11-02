import pytest
from fastapi.testclient import TestClient

from main import app
from app.auth import router as auth_router
from app.auth.security import create_access_token

client = TestClient(app)

PROTECTED = [
    "/api/dashboard/summary", "/api/machines", "/api/alerts",
    "/api/recommendations", "/api/schemes", "/api/auth/me",
    "/api/orders/",
]


@pytest.mark.parametrize("path", PROTECTED)
def test_protected_routes_require_token(path):
    assert client.get(path).status_code == 401


def test_garbage_token_rejected():
    r = client.get("/api/machines", headers={"Authorization": "Bearer nonsense"})
    assert r.status_code == 401


def test_login_success(monkeypatch):
    monkeypatch.setattr(
        auth_router, "authenticate_user",
        lambda e, p: {"id": 1, "email": e, "full_name": "T", "role": "admin"},
    )
    r = client.post("/api/auth/login", json={"email": "a@b.com", "password": "x"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["expires_in"] == 1800


def test_login_failure(monkeypatch):
    monkeypatch.setattr(auth_router, "authenticate_user", lambda e, p: None)
    r = client.post("/api/auth/login", json={"email": "a@b.com", "password": "bad"})
    assert r.status_code == 401


def test_me_with_valid_token(monkeypatch):
    class FakeCur:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def execute(self, *a, **k): pass
        def fetchone(self): return (1, "a@b.com", "Test User", "admin", True)

    class FakeConn:
        def cursor(self): return FakeCur()
        def close(self): pass

    monkeypatch.setattr("app.database.connection.get_connection", lambda: FakeConn())
    token = create_access_token(1, "admin")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"