import statistics
import time

import pytest
from fastapi.testclient import TestClient

from app.core.db import _DB
from app.main import app

client = TestClient(app)

USER = {"X-Auth-Token": "token123"}
OTHER = {"X-Auth-Token": "token456"}


@pytest.fixture(autouse=True)
def clear_db():
    _DB["wishes"].clear()


def test_nfr01_protected_endpoints_require_token():
    r = client.get("/wishes")
    assert r.status_code == 401
    body = r.json()
    assert body["error"]["code"] == "http_error"
    assert "unauthorized" in body["error"]["message"]


def test_nfr02_validation_422_with_unified_json():
    long_title = "X" * 51
    r = client.post(
        "/wishes",
        json={"id": 1, "title": long_title, "price_estimate": 10},
        headers=USER,
    )
    assert r.status_code == 422
    body = r.json()
    assert "error" in body
    assert body["error"]["code"] == "validation_error"


def test_nfr03_error_format_is_uniform_for_not_found():
    client.post("/wishes", json={"id": 1, "title": "A"}, headers=USER)
    r = client.get("/wishes/1", headers=OTHER)
    assert r.status_code == 404
    body = r.json()
    assert isinstance(body, dict)
    assert "error" in body
    assert set(body["error"].keys()) == {"code", "message"}
    assert body["error"]["code"] == "not_found"


def test_nfr04_sorted_endpoint_p95_under_threshold():
    for i in range(1, 51):
        client.post(
            "/wishes",
            json={"id": i, "title": f"W{i}", "price_estimate": i * 1.0},
            headers=USER,
        )

    durations = []
    for _ in range(60):
        t0 = time.perf_counter()
        r = client.get(
            "/wishes/sorted", params={"order_by": "price_estimate"}, headers=USER
        )
        t1 = time.perf_counter()
        assert r.status_code == 200
        durations.append((t1 - t0) * 1000.0)

    durations.sort()
    # p95
    idx = max(0, int(len(durations) * 0.95) - 1)
    p95_ms = durations[idx]

    assert p95_ms <= 300.0, f"p95 too high: {p95_ms:.1f} ms"


@pytest.mark.skip(reason="NFR-05 проверяется отчётами SCA (Dependabot/Snyk) в CI.")
def test_nfr05_sca_sla_checked_in_ci():
    pass


def test_nfr06_db_consistency_on_failed_put_and_duplicate_create():
    r1 = client.post("/wishes", json={"id": 1, "title": "A"}, headers=USER)
    assert r1.status_code == 200
    before = list(_DB["wishes"])

    r2 = client.put("/wishes/999", json={"id": 999, "title": "X"}, headers=USER)
    assert r2.status_code == 404
    assert _DB["wishes"] == before

    r3 = client.post("/wishes", json={"id": 1, "title": "Dup"}, headers=USER)
    assert r3.status_code == 422
    records = [w for w in _DB["wishes"] if w["owner"] == "alice" and w["id"] == 1]
    assert len(records) == 1


def test_nfr07_no_pii_in_logs_on_error(caplog):
    caplog.clear()
    _ = client.get("/wishes/777", headers=USER)
    assert "token123" not in caplog.text


def test_nfr08_health_latency_under_threshold():
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        r = client.get("/health")
        t1 = time.perf_counter()
        assert r.status_code == 200
        times.append((t1 - t0) * 1000.0)

    avg_ms = statistics.mean(times)
    assert avg_ms <= 200.0, f"/health too slow on average: {avg_ms:.1f} ms"
