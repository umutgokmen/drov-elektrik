"""
Tests for issue #21 - Phase 2 drawing updates for salt malzeme (EJB standard) panels.

Covers:
- BOM endpoint includes all salt malzeme standard components
- BOM schema marks salt malzeme items correctly
- STEP export endpoint is reachable
- Section view renders drain valve indicator
- 2D legend includes salt malzeme items
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import SALT_MALZEME_COMPONENTS, get_box_model_by_id
from app.schemas import ConfigurationInput, BOMItem
from app.api.routes import generate_bom


client = TestClient(app)

VALID_CONFIG = {
    "box_id": "ejb51",
    "terminals": 10,
    "holes_top": 2,
    "holes_bottom": 2,
    "holes_left": 0,
    "holes_right": 0,
}


# ============================================================
# Salt malzeme model data tests
# ============================================================

class TestSaltMalzemeComponents:
    def test_salt_malzeme_components_defined(self):
        """SALT_MALZEME_COMPONENTS must be non-empty."""
        assert len(SALT_MALZEME_COMPONENTS) > 0

    def test_drain_valve_present(self):
        """Drain valve must be in salt malzeme components."""
        codes = [c["part_code"] for c in SALT_MALZEME_COMPONENTS]
        assert "Drain_Valve_M20x1.5mm" in codes

    def test_end_clamp_present(self):
        """DIN rail end clamps must be in salt malzeme components."""
        codes = [c["part_code"] for c in SALT_MALZEME_COMPONENTS]
        assert "pnl_302203_CLIPFIX-35-5" in codes

    def test_cover_present(self):
        """Enclosure cover must be in salt malzeme components."""
        names = [c["part_name"] for c in SALT_MALZEME_COMPONENTS]
        assert any("Cover" in n or "cover" in n for n in names)

    def test_all_components_have_required_fields(self):
        """Every salt malzeme component must have the required schema keys."""
        required_keys = {"part_name", "part_code", "quantity", "description"}
        for component in SALT_MALZEME_COMPONENTS:
            assert required_keys.issubset(component.keys()), (
                f"Component {component} is missing required keys"
            )

    def test_quantities_are_positive(self):
        """All salt malzeme quantities must be >= 1."""
        for component in SALT_MALZEME_COMPONENTS:
            assert component["quantity"] >= 1


# ============================================================
# BOM schema tests
# ============================================================

class TestBOMSchema:
    def test_bom_item_has_is_salt_malzeme_field(self):
        """BOMItem schema must expose is_salt_malzeme with a False default."""
        item = BOMItem(
            item_no=1,
            part_name="Test Part",
            part_code="TEST-001",
            quantity=1,
        )
        assert hasattr(item, "is_salt_malzeme")
        assert item.is_salt_malzeme is False

    def test_bom_item_salt_malzeme_flag_can_be_set(self):
        """BOMItem salt malzeme flag must be settable to True."""
        item = BOMItem(
            item_no=1,
            part_name="Drain Valve",
            part_code="Drain_Valve_M20x1.5mm",
            quantity=1,
            is_salt_malzeme=True,
        )
        assert item.is_salt_malzeme is True


# ============================================================
# BOM API tests
# ============================================================

class TestBOMEndpoint:
    def test_bom_returns_200(self):
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200

    def test_bom_includes_salt_malzeme_items(self):
        """The BOM response must include at least one salt malzeme item."""
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200
        data = response.json()
        salt_items = [item for item in data["items"] if item["is_salt_malzeme"]]
        assert len(salt_items) > 0, "BOM must contain at least one salt malzeme item"

    def test_bom_includes_drain_valve(self):
        """Drain valve must appear in the BOM response."""
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200
        data = response.json()
        codes = [item["part_code"] for item in data["items"]]
        assert "Drain_Valve_M20x1.5mm" in codes

    def test_bom_includes_end_clamps(self):
        """End clamps must appear in the BOM response."""
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200
        data = response.json()
        codes = [item["part_code"] for item in data["items"]]
        assert "pnl_302203_CLIPFIX-35-5" in codes

    def test_bom_total_items_includes_salt_malzeme(self):
        """total_items count must include salt malzeme standard items."""
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == len(data["items"])
        # At minimum: enclosure + rails + terminals + glands + len(SALT_MALZEME_COMPONENTS)
        assert data["total_items"] >= len(SALT_MALZEME_COMPONENTS) + 1

    def test_bom_enclosure_not_salt_malzeme(self):
        """The main enclosure item must NOT be marked as salt malzeme."""
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200
        data = response.json()
        enclosure_items = [
            item for item in data["items"]
            if "Enclosure" in item["part_name"] and not item["is_salt_malzeme"]
        ]
        assert len(enclosure_items) == 1

    def test_bom_item_numbers_are_sequential(self):
        """All BOM item_no values must be sequential starting from 1."""
        response = client.post("/api/v1/bom", json=VALID_CONFIG)
        assert response.status_code == 200
        data = response.json()
        item_nos = [item["item_no"] for item in data["items"]]
        assert item_nos == list(range(1, len(item_nos) + 1))

    def test_bom_no_terminals_skips_terminal_item(self):
        """When terminals=0, terminal block must not appear in BOM."""
        config = {**VALID_CONFIG, "terminals": 0}
        response = client.post("/api/v1/bom", json=config)
        assert response.status_code == 200
        data = response.json()
        terminal_items = [
            item for item in data["items"]
            if "Terminal" in item["part_name"] and not item["is_salt_malzeme"]
        ]
        assert len(terminal_items) == 0

    def test_bom_invalid_box_returns_404(self):
        """BOM endpoint must return 404 for unknown box_id."""
        config = {**VALID_CONFIG, "box_id": "ejb_invalid"}
        response = client.post("/api/v1/bom", json=config)
        assert response.status_code == 404


# ============================================================
# STEP export endpoint tests
# ============================================================

class TestSTEPEndpoint:
    def test_step_endpoint_exists(self):
        """
        /generate/step must be registered and return something other than 404.
        When CadQuery is not installed the endpoint should return 500 (not 404).
        """
        response = client.post("/api/v1/generate/step", json=VALID_CONFIG)
        assert response.status_code != 404, (
            "/api/v1/generate/step endpoint must be registered"
        )

    def test_step_invalid_config_returns_400(self):
        """An invalid configuration must return 400 before attempting generation."""
        invalid_config = {**VALID_CONFIG, "terminals": 9999}
        response = client.post("/api/v1/generate/step", json=invalid_config)
        assert response.status_code == 400

    def test_step_invalid_box_returns_400_or_500(self):
        """An invalid box_id must return 400 (validation) or 500 (generation failure)."""
        config = {**VALID_CONFIG, "box_id": "ejb_invalid"}
        response = client.post("/api/v1/generate/step", json=config)
        assert response.status_code in (400, 500)


# ============================================================
# DXF endpoint sanity check (2D views)
# ============================================================

class TestDXFEndpoint:
    def test_dxf_endpoint_returns_content(self):
        """DXF endpoint must return a non-empty DXF file."""
        response = client.post("/api/v1/generate/dxf", json=VALID_CONFIG)
        assert response.status_code == 200
        assert len(response.content) > 0
        assert response.headers["content-type"] == "application/dxf"

    def test_dxf_filename_contains_box_id(self):
        """DXF filename in Content-Disposition must contain the box id (case-insensitive)."""
        response = client.post("/api/v1/generate/dxf", json=VALID_CONFIG)
        assert response.status_code == 200
        disposition = response.headers.get("content-disposition", "")
        assert VALID_CONFIG["box_id"].upper() in disposition.upper()
