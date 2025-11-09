from __future__ import annotations

import json

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


def test_wish_rejects_extra_fields():
    payload = {"id": 1, "title": "Book", "price_estimate": 10.00, "extra": "oops"}
    r = client.post("/wishes", json=payload, headers=USER)
    assert r.status_code == 422


def test_decimal_disallows_more_than_two_fraction_digits():
    payload = {"id": 1, "title": "X", "price_estimate": 10.123}
    r = client.post("/wishes", json=payload, headers=USER)
    assert r.status_code == 422


def test_decimal_filtering_with_query_decimal():
    client.post(
        "/wishes", json={"id": 1, "title": "A", "price_estimate": "9.99"}, headers=USER
    )
    client.post(
        "/wishes", json={"id": 2, "title": "B", "price_estimate": "15.00"}, headers=USER
    )

    r_less = client.get("/wishes/price/less", params={"price": "10.00"}, headers=USER)
    assert r_less.status_code == 200
    assert [w["id"] for w in r_less.json()] == [1]

    r_greater = client.get(
        "/wishes/price/greater", params={"price": "10.00"}, headers=USER
    )
    assert r_greater.status_code == 200
    assert [w["id"] for w in r_greater.json()] == [2]


def test_rfc7807_on_validation_error_when_requested():
    r = client.post(
        "/wishes",
        json={"id": 1, "title": "A" * 51},
        headers={"X-Auth-Token": "token123", "Accept": "application/problem+json"},
    )
    assert r.status_code == 422
    body = r.json()
    for k in ("type", "title", "status", "detail", "correlation_id"):
        assert k in body
    assert body["status"] == 422


def test_import_atomic_validation_and_schema_enforced():
    bad_backup = [{"id": 1, "title": "OK"}, {"id": 2, "no_title": "bad"}]
    r = client.post("/wishes/import", json={"backup": bad_backup}, headers=USER)
    assert r.status_code in (422, 400)
    assert _DB["wishes"] == []


def test_import_body_size_limit_enforced():
    big = {"backup": [{"id": i, "title": "X"} for i in range(120_000)]}
    raw = json.dumps(big).encode("utf-8")
    r = client.post(
        "/wishes/import",
        data=raw,
        headers={"Content-Type": "application/json", **USER},
    )
    assert r.status_code == 413


def test_import_decimal_precision_preserved():
    backup = [
        {"id": 1, "title": "A", "price_estimate": 0.10},
        {"id": 2, "title": "B", "price_estimate": 0.20},
    ]
    r = client.post("/wishes/import", json={"backup": backup}, headers=USER)
    assert r.status_code == 200

    listed = client.get("/wishes", headers=USER).json()
    assert listed[0]["price_estimate"] in ("0.10", "0.1")
    assert listed[1]["price_estimate"] in ("0.20", "0.2")
