"""
Tests for issue #30 - Order save and history endpoints.

Covers:
- POST /orders saves a configuration and returns it with an ID
- GET /orders returns all saved orders
- GET /orders/{id} returns a single order
- 404 for unknown box_id or order_id
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine


@pytest.fixture(autouse=True)
def reset_db():
    """Recreate tables before each test to ensure a clean state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

VALID_ORDER = {
    "box_id": "ejb51",
    "terminals": 10,
    "holes_top": 2,
    "holes_bottom": 1,
    "holes_left": 0,
    "holes_right": 0,
}


class TestSaveOrder:
    def test_save_order_returns_201(self):
        response = client.post("/api/v1/orders", json=VALID_ORDER)
        assert response.status_code == 201

    def test_save_order_returns_id(self):
        response = client.post("/api/v1/orders", json=VALID_ORDER)
        data = response.json()
        assert "id" in data
        assert data["id"] >= 1

    def test_save_order_stores_config_fields(self):
        response = client.post("/api/v1/orders", json=VALID_ORDER)
        data = response.json()
        assert data["box_id"] == VALID_ORDER["box_id"]
        assert data["terminals"] == VALID_ORDER["terminals"]
        assert data["holes_top"] == VALID_ORDER["holes_top"]
        assert data["holes_bottom"] == VALID_ORDER["holes_bottom"]
        assert data["holes_left"] == VALID_ORDER["holes_left"]
        assert data["holes_right"] == VALID_ORDER["holes_right"]

    def test_save_order_stores_optional_name(self):
        payload = {**VALID_ORDER, "name": "Test Order Alpha"}
        response = client.post("/api/v1/orders", json=payload)
        assert response.status_code == 201
        assert response.json()["name"] == "Test Order Alpha"

    def test_save_order_name_defaults_to_null(self):
        response = client.post("/api/v1/orders", json=VALID_ORDER)
        assert response.json()["name"] is None

    def test_save_order_has_created_at(self):
        response = client.post("/api/v1/orders", json=VALID_ORDER)
        assert "created_at" in response.json()
        assert response.json()["created_at"] is not None

    def test_save_order_invalid_box_returns_404(self):
        payload = {**VALID_ORDER, "box_id": "ejb_invalid"}
        response = client.post("/api/v1/orders", json=payload)
        assert response.status_code == 404


class TestListOrders:
    def test_list_orders_empty(self):
        response = client.get("/api/v1/orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_orders_returns_saved(self):
        client.post("/api/v1/orders", json=VALID_ORDER)
        response = client.get("/api/v1/orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["box_id"] == VALID_ORDER["box_id"]

    def test_list_orders_newest_first(self):
        payload_a = {**VALID_ORDER, "name": "A"}
        payload_b = {**VALID_ORDER, "name": "B"}
        client.post("/api/v1/orders", json=payload_a)
        client.post("/api/v1/orders", json=payload_b)
        response = client.get("/api/v1/orders")
        data = response.json()
        assert len(data) == 2
        # Newest (B) should appear first
        assert data[0]["name"] == "B"
        assert data[1]["name"] == "A"


class TestGetOrder:
    def test_get_order_returns_200(self):
        saved = client.post("/api/v1/orders", json=VALID_ORDER).json()
        response = client.get(f"/api/v1/orders/{saved['id']}")
        assert response.status_code == 200

    def test_get_order_returns_correct_data(self):
        saved = client.post("/api/v1/orders", json=VALID_ORDER).json()
        response = client.get(f"/api/v1/orders/{saved['id']}")
        data = response.json()
        assert data["id"] == saved["id"]
        assert data["box_id"] == VALID_ORDER["box_id"]
        assert data["terminals"] == VALID_ORDER["terminals"]

    def test_get_order_unknown_id_returns_404(self):
        response = client.get("/api/v1/orders/9999")
        assert response.status_code == 404
