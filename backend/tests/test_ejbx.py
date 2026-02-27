"""
Tests for issue #26 - EJBX box type integration.

Covers:
- EJBX model data existence and schema compliance
- EJBX-specific hole clearance and edge margin rules
- Validation service enforces stricter EJBX limits
- BOM, PDF, and STEP endpoints reachable with EJBX box IDs
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import EJBX_MODELS_DATA, get_box_model_by_id
from app.schemas import ConfigurationInput
from app.services.validation.validation_service import (
    MIN_EJBX_HOLE_CLEARANCE,
    MIN_EJBX_EDGE_MARGIN,
    MIN_HOLE_CLEARANCE,
    MIN_EDGE_MARGIN,
    validate_hole_placement,
    run_full_validation,
)

client = TestClient(app)

VALID_EJBX_CONFIG = {
    "box_id": "ejbx2",
    "terminals": 5,
    "holes_top": 1,
    "holes_bottom": 1,
    "holes_left": 0,
    "holes_right": 0,
}

ALL_EJBX_IDS = [m["id"] for m in EJBX_MODELS_DATA]


# ============================================================
# EJBX model data tests
# ============================================================

class TestEJBXModelData:
    def test_ejbx_models_defined(self):
        """EJBX_MODELS_DATA must be non-empty."""
        assert len(EJBX_MODELS_DATA) > 0

    def test_ejbx_model_ids_start_with_ejbx(self):
        """All EJBX model IDs must start with 'ejbx'."""
        for model in EJBX_MODELS_DATA:
            assert model["id"].startswith("ejbx"), (
                f"Expected EJBX model id to start with 'ejbx', got: {model['id']}"
            )

    def test_ejbx_models_have_required_fields(self):
        """Every EJBX model must have all required schema fields."""
        required_keys = {
            "id", "name", "internal_length", "internal_width", "internal_depth",
            "mounting_plate_x", "mounting_plate_y",
            "max_holes_long", "max_holes_short", "rail_count", "max_terminals",
        }
        for model in EJBX_MODELS_DATA:
            assert required_keys.issubset(model.keys()), (
                f"Model {model['id']} is missing required keys"
            )

    def test_ejbx_models_positive_dimensions(self):
        """All EJBX dimension fields must be positive."""
        for model in EJBX_MODELS_DATA:
            assert model["internal_length"] > 0
            assert model["internal_width"] > 0
            assert model["internal_depth"] > 0
            assert model["mounting_plate_x"] > 0
            assert model["mounting_plate_y"] > 0

    def test_ejbx_models_loadable_by_id(self):
        """get_box_model_by_id must return a BoxModel for each EJBX model."""
        for model in EJBX_MODELS_DATA:
            box = get_box_model_by_id(model["id"])
            assert box is not None, f"Could not load EJBX model: {model['id']}"
            assert box.id == model["id"]

    def test_ejbx_boxes_endpoint_lists_ejbx(self):
        """GET /boxes must include at least one EJBX model."""
        response = client.get("/api/v1/boxes")
        assert response.status_code == 200
        ids = [b["id"] for b in response.json()]
        ejbx_ids = [i for i in ids if i.startswith("ejbx")]
        assert len(ejbx_ids) > 0, "No EJBX models found in /boxes response"

    def test_ejbx_box_detail_endpoint(self):
        """GET /boxes/ejbx1 must return the ejbx1 model."""
        response = client.get("/api/v1/boxes/ejbx1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "ejbx1"


# ============================================================
# EJBX engineering constants tests
# ============================================================

class TestEJBXConstants:
    def test_ejbx_hole_clearance_larger_than_ejb(self):
        """EJBX hole clearance must be stricter than standard EJB clearance."""
        assert MIN_EJBX_HOLE_CLEARANCE > MIN_HOLE_CLEARANCE

    def test_ejbx_edge_margin_larger_than_ejb(self):
        """EJBX edge margin must be stricter than standard EJB edge margin."""
        assert MIN_EJBX_EDGE_MARGIN > MIN_EDGE_MARGIN


# ============================================================
# EJBX validation rule tests
# ============================================================

class TestEJBXValidationRules:
    def test_ejbx_hole_placement_uses_stricter_rules(self):
        """
        With identical side length, EJBX allows fewer holes than EJB
        due to stricter clearance and edge margin.
        """
        side_length = 300.0
        # Use a count guaranteed to exceed physical limits for both EJB and EJBX,
        # so the max-possible calculation is always exercised.
        large_count = 999
        _, _, ejb_max = validate_hole_placement(
            large_count, side_length, MIN_HOLE_CLEARANCE, MIN_EDGE_MARGIN
        )
        _, _, ejbx_max = validate_hole_placement(
            large_count, side_length, MIN_EJBX_HOLE_CLEARANCE, MIN_EJBX_EDGE_MARGIN
        )
        assert ejbx_max < ejb_max

    def test_valid_ejbx_config_passes(self):
        """A valid EJBX configuration must pass validation."""
        config = ConfigurationInput(**VALID_EJBX_CONFIG)
        result = run_full_validation(config)
        assert result.is_valid, f"Validation errors: {result.errors}"

    def test_ejbx_too_many_holes_fails(self):
        """Exceeding EJBX physical hole limits must produce a validation error."""
        config = ConfigurationInput(
            box_id="ejbx1",
            terminals=0,
            holes_top=99,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        error_fields = [e.field for e in result.errors]
        assert "holes_top" in error_fields

    def test_ejbx_too_many_terminals_fails(self):
        """Exceeding EJBX terminal capacity must produce a validation error."""
        box = get_box_model_by_id("ejbx1")
        config = ConfigurationInput(
            box_id="ejbx1",
            terminals=box.max_terminals + 1,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        error_fields = [e.field for e in result.errors]
        assert "terminals" in error_fields

    @pytest.mark.parametrize("box_id", ALL_EJBX_IDS)
    def test_all_ejbx_models_pass_with_single_hole(self, box_id):
        """A minimal valid config (1 hole per side, 1 terminal) must pass for every EJBX model."""
        config = ConfigurationInput(
            box_id=box_id,
            terminals=1,
            holes_top=1,
            holes_bottom=1,
            holes_left=1,
            holes_right=1,
        )
        result = run_full_validation(config)
        assert result.is_valid, (
            f"Expected valid config for {box_id} to pass; errors: {result.errors}"
        )

    @pytest.mark.parametrize("box_id", ALL_EJBX_IDS)
    def test_all_ejbx_models_reject_excess_holes(self, box_id):
        """An absurdly large hole count must fail for every EJBX model."""
        config = ConfigurationInput(
            box_id=box_id,
            terminals=0,
            holes_top=999,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        error_fields = [e.field for e in result.errors]
        assert "holes_top" in error_fields

    def test_validate_endpoint_accepts_ejbx(self):
        """POST /validate must return 200 and is_valid=true for a valid EJBX config."""
        response = client.post("/api/v1/validate", json=VALID_EJBX_CONFIG)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_validate_endpoint_rejects_ejbx_excess_holes(self):
        """POST /validate must flag an error for too many holes on an EJBX box."""
        config = {**VALID_EJBX_CONFIG, "holes_top": 99}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        error_fields = [e["field"] for e in data["errors"]]
        assert "holes_top" in error_fields


# ============================================================
# EJBX BOM endpoint tests
# ============================================================

class TestEJBXBOMEndpoint:
    def test_bom_returns_200_for_ejbx(self):
        """BOM endpoint must return 200 for a valid EJBX configuration."""
        response = client.post("/api/v1/bom", json=VALID_EJBX_CONFIG)
        assert response.status_code == 200

    def test_bom_enclosure_name_contains_ejbx(self):
        """BOM must list the EJBX enclosure as the first non-salt-malzeme item."""
        response = client.post("/api/v1/bom", json=VALID_EJBX_CONFIG)
        assert response.status_code == 200
        data = response.json()
        enclosure_items = [
            item for item in data["items"]
            if "Enclosure" in item["part_name"] and not item["is_salt_malzeme"]
        ]
        assert len(enclosure_items) == 1
        assert "EJBX" in enclosure_items[0]["part_name"].upper()


# ============================================================
# EJBX PDF / STEP endpoint tests
# ============================================================

class TestEJBXOutputEndpoints:
    def test_pdf_endpoint_accepts_ejbx(self):
        """POST /generate/pdf must return 200 for a valid EJBX config."""
        response = client.post("/api/v1/generate/pdf", json=VALID_EJBX_CONFIG)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_dxf_endpoint_accepts_ejbx(self):
        """POST /generate/dxf must return a non-empty DXF for a valid EJBX config."""
        response = client.post("/api/v1/generate/dxf", json=VALID_EJBX_CONFIG)
        assert response.status_code == 200
        assert len(response.content) > 0
        assert response.headers["content-type"] == "application/dxf"

    def test_step_endpoint_registered_for_ejbx(self):
        """
        POST /generate/step must be registered; returns something other than 404.
        When CadQuery is not installed the endpoint should return 500, not 404.
        """
        response = client.post("/api/v1/generate/step", json=VALID_EJBX_CONFIG)
        assert response.status_code != 404, (
            "/api/v1/generate/step endpoint must be registered"
        )

    def test_pdf_invalid_ejbx_config_returns_400(self):
        """POST /generate/pdf must return 400 when EJBX config is invalid."""
        invalid_config = {**VALID_EJBX_CONFIG, "holes_top": 99}
        response = client.post("/api/v1/generate/pdf", json=invalid_config)
        assert response.status_code == 400
