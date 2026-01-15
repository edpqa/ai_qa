import pytest

from app.app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_items_initially_empty(client):
    r = client.get("/items")
    assert r.status_code == 200
    assert r.get_json() == {"items": []}


def test_create_item_requires_name(client):
    r = client.post("/items", json={})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_create_item_success(client):
    r = client.post("/items", json={"name": "  first  "})
    assert r.status_code == 201
    created = r.get_json()
    assert created["id"] == 1
    assert created["name"] == "first"

    r2 = client.get("/items")
    assert r2.status_code == 200
    items = r2.get_json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "first"