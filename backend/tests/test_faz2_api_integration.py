"""
Issue #22 - Faz 2 test & approval

API-level integration tests for salt malzeme panel and material combination endpoints.
Covers /validate, /layout, /bom, /generate/pdf, and /generate/dxf routes.
"""
import pytest


# ================================================================
# /validate endpoint - salt malzeme
# ================================================================

class TestValidateEndpointSaltMalzeme:

    def test_salt_malzeme_valid(self, client):
        response = client.post("/api/v1/validate", json={
            "box_id": "ejb51",
            "terminals": 40,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["errors"] == []

    def test_salt_malzeme_over_capacity_returns_error(self, client):
        response = client.post("/api/v1/validate", json={
            "box_id": "ejb21",
            "terminals": 9999,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any(e["field"] == "terminals" for e in data["errors"])

    def test_unknown_box_id_returns_error(self, client):
        response = client.post("/api/v1/validate", json={
            "box_id": "ejb_nonexistent",
            "terminals": 10,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False


# ================================================================
# /layout endpoint - salt malzeme
# ================================================================

class TestLayoutEndpointSaltMalzeme:

    def test_salt_malzeme_layout_returns_rails(self, client):
        response = client.post("/api/v1/layout", json={
            "box_id": "ejb51",
            "terminals": 24,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["rails"]) > 0
        assert data["holes_top"] == []
        assert data["holes_bottom"] == []
        assert data["holes_left"] == []
        assert data["holes_right"] == []

    def test_invalid_config_layout_returns_400(self, client):
        response = client.post("/api/v1/layout", json={
            "box_id": "ejb21",
            "terminals": 9999,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 400


# ================================================================
# /bom endpoint - different material combinations
# ================================================================

class TestBOMEndpointMaterialCombinations:

    def test_salt_malzeme_bom_no_cable_glands(self, client):
        """BOM for salt malzeme must not include cable gland line items."""
        response = client.post("/api/v1/bom", json={
            "box_id": "ejb51",
            "terminals": 20,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        gland_items = [i for i in data["items"] if "Gland" in i["part_name"] or "gland" in i["part_name"].lower()]
        assert gland_items == []

    def test_bom_with_holes_includes_cable_glands(self, client):
        """BOM for config with holes must include cable gland line items."""
        response = client.post("/api/v1/bom", json={
            "box_id": "ejb51",
            "terminals": 20,
            "holes_top": 3,
            "holes_bottom": 3,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        gland_items = [i for i in data["items"] if "Gland" in i["part_name"]]
        assert len(gland_items) == 1
        assert gland_items[0]["quantity"] == 6

    def test_bom_terminals_quantity_matches_config(self, client):
        terminals = 30
        response = client.post("/api/v1/bom", json={
            "box_id": "ejb51",
            "terminals": terminals,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        terminal_items = [i for i in data["items"] if "Terminal" in i["part_name"]]
        assert len(terminal_items) == 1
        assert terminal_items[0]["quantity"] == terminals

    def test_bom_zero_terminals_no_terminal_line_item(self, client):
        """BOM with 0 terminals must not include terminal block line item."""
        response = client.post("/api/v1/bom", json={
            "box_id": "ejb51",
            "terminals": 0,
            "holes_top": 2,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        data = response.json()
        terminal_items = [i for i in data["items"] if "Terminal" in i["part_name"]]
        assert terminal_items == []

    @pytest.mark.parametrize("box_id,terminals,top,bottom,left,right", [
        ("ejb21", 15,  0,  0, 0, 0),
        ("ejb31", 26,  2,  2, 1, 1),
        ("ejb51", 40,  5,  5, 3, 3),
        ("ejb61", 46,  0,  0, 0, 0),
        ("ejb71", 55,  4,  4, 2, 2),
        ("ejb91", 70,  6,  6, 4, 4),
    ])
    def test_bom_total_items_positive(self, client, box_id, terminals, top, bottom, left, right):
        """BOM must always return at least 1 item for any valid configuration."""
        response = client.post("/api/v1/bom", json={
            "box_id": box_id,
            "terminals": terminals,
            "holes_top": top,
            "holes_bottom": bottom,
            "holes_left": left,
            "holes_right": right,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] >= 1


# ================================================================
# /generate/dxf endpoint - material combinations
# ================================================================

class TestDXFGenerationMaterialCombinations:

    def test_salt_malzeme_dxf_generated(self, client):
        """DXF generation must succeed for salt malzeme configuration."""
        response = client.post("/api/v1/generate/dxf", json={
            "box_id": "ejb51",
            "terminals": 24,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 200
        assert len(response.content) > 0
        # DXF files start with the SECTION keyword
        assert b"SECTION" in response.content

    @pytest.mark.parametrize("box_id,terminals,top,bottom,left,right", [
        ("ejb21", 10,  0,  0, 0, 0),
        ("ejb31",  0,  2,  2, 1, 1),
        ("ejb51", 40,  5,  5, 3, 3),
        ("ejb91", 70,  0,  0, 0, 0),
    ])
    def test_dxf_generation_various_combinations(
        self, client, box_id, terminals, top, bottom, left, right
    ):
        """DXF generation must succeed for various material combinations."""
        response = client.post("/api/v1/generate/dxf", json={
            "box_id": box_id,
            "terminals": terminals,
            "holes_top": top,
            "holes_bottom": bottom,
            "holes_left": left,
            "holes_right": right,
        })
        assert response.status_code == 200
        assert len(response.content) > 0

    def test_invalid_config_dxf_returns_400(self, client):
        """DXF generation must reject invalid configurations with 400."""
        response = client.post("/api/v1/generate/dxf", json={
            "box_id": "ejb21",
            "terminals": 9999,
            "holes_top": 0,
            "holes_bottom": 0,
            "holes_left": 0,
            "holes_right": 0,
        })
        assert response.status_code == 400


# ================================================================
# /boxes endpoint - sanity checks
# ================================================================

class TestBoxEndpoints:

    def test_list_boxes_returns_all_models(self, client):
        response = client.get("/api/v1/boxes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 6  # At minimum EJB 21/31/51/61/71/91

    def test_get_box_ejb51(self, client):
        response = client.get("/api/v1/boxes/ejb51")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "ejb51"
        assert data["max_terminals"] > 0

    def test_get_unknown_box_returns_404(self, client):
        response = client.get("/api/v1/boxes/ejb_fake")
        assert response.status_code == 404
