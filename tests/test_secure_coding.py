from fastapi.testclient import TestClient

from app.core.db import _DB
from app.core.secrets import SecretsProvider
from app.main import app

client = TestClient(app)
USER = {"X-Auth-Token": "token123"}


def setup_function(_):
    _DB["wishes"].clear()


def test_import_too_large_returns_413():
    big_backup = [{"id": i, "title": f"W{i}"} for i in range(6001)]
    r = client.post("/wishes/import", json={"backup": big_backup}, headers=USER)
    assert r.status_code == 413
    body = r.json()
    assert ("error" in body and "code" in body["error"]) or all(
        k in body for k in ("type", "title", "status", "detail")
    )


def test_import_invalid_schema_returns_422():
    bad_data = {"backup": [{"no_title": "oops"}]}
    r = client.post("/wishes/import", json=bad_data, headers=USER)
    assert r.status_code == 422
    body = r.json()
    assert ("error" in body and body["error"]["code"] == "validation_error") or (
        body.get("status") == 422
    )


def test_import_exact_limit_is_ok():
    backup = [{"id": i, "title": f"W{i}"} for i in range(5000)]
    r = client.post("/wishes/import", json={"backup": backup}, headers=USER)
    assert r.status_code == 200
    assert r.json()["count"] == 5000


def test_rfc7807_format_on_http_error_when_requested():
    r = client.get(
        "/wishes", headers={"X-Auth-Token": "bad", "Accept": "application/problem+json"}
    )
    assert r.status_code == 401
    body = r.json()
    assert all(
        k in body for k in ("type", "title", "status", "detail", "correlation_id")
    )
    assert body["status"] == 401


def test_rfc7807_on_app_error_when_requested():
    r = client.get(
        "/wishes/sorted",
        params={"order_by": "invalid"},
        headers={"X-Auth-Token": "token123", "Accept": "application/problem+json"},
    )
    assert r.status_code == 422
    body = r.json()
    assert all(
        k in body for k in ("type", "title", "status", "detail", "correlation_id")
    )
    assert body["status"] == 422


def test_secrets_provider_from_env_json(monkeypatch):
    mp = {"t1": "u1", "t2": "u2"}
    monkeypatch.setenv("VAULT_TOKEN_MAP_JSON", '{"t1":"u1","t2":"u2"}')
    sp = SecretsProvider()
    assert sp.get_token_map() == mp
