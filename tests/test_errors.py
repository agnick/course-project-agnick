import pytest
from fastapi.testclient import TestClient

from app.core.db import _DB
from app.main import app

client = TestClient(app)

USER_TOKEN = {"X-Auth-Token": "token123"}
OTHER_TOKEN = {"X-Auth-Token": "token456"}


@pytest.fixture(autouse=True)
def clear_db():
    _DB["wishes"].clear()


def test_unauthorized_access_returns_401():
    r = client.get("/wishes")
    assert r.status_code == 401
    body = r.json()
    assert body["error"]["code"] == "http_error"
    assert "unauthorized" in body["error"]["message"]


def test_owner_only_access():
    wish = {"id": 1, "title": "Book", "price_estimate": 100}
    r1 = client.post("/wishes", json=wish, headers=USER_TOKEN)
    assert r1.status_code == 200

    r2 = client.get("/wishes/1", headers=OTHER_TOKEN)
    assert r2.status_code == 404
    body = r2.json()
    assert body["error"]["code"] == "not_found"


def test_validation_error_duplicate_id_per_user():
    wish = {"id": 1, "title": "Book", "price_estimate": 10.0}
    r1 = client.post("/wishes", json=wish, headers=USER_TOKEN)
    assert r1.status_code == 200

    r2 = client.post("/wishes", json=wish, headers=USER_TOKEN)
    assert r2.status_code == 422
    body = r2.json()
    assert body["error"]["code"] == "validation_error"


def test_validation_error_invalid_title_length():
    long_title = "A" * 51
    r = client.post(
        "/wishes",
        json={"id": 1, "title": long_title, "price_estimate": 100},
        headers=USER_TOKEN,
    )
    assert r.status_code == 422
    body = r.json()
    assert "error" in body or "detail" in body


def test_validation_error_negative_price():
    r = client.post(
        "/wishes",
        json={"id": 2, "title": "Cheap", "price_estimate": -10},
        headers=USER_TOKEN,
    )
    assert r.status_code == 422


def test_not_found_wish_returns_404():
    r = client.get("/wishes/999", headers=USER_TOKEN)
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_delete_nonexistent_wish_returns_404():
    r = client.delete("/wishes/999", headers=USER_TOKEN)
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "not_found"


def test_error_format_is_uniform():
    client.post("/wishes", json={"id": 1, "title": "X"}, headers=USER_TOKEN)
    r = client.delete("/wishes/1", headers=OTHER_TOKEN)
    assert r.status_code == 404
    body = r.json()
    assert isinstance(body, dict)
    assert "error" in body
    assert set(body["error"].keys()) == {"code", "message"}


def test_invalid_sort_key_returns_validation_error():
    r = client.get("/wishes/sorted", params={"order_by": "invalid"}, headers=USER_TOKEN)
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
