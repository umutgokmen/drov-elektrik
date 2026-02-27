"""
Tests for issue #27 - EJC box type integration.

Covers:
- EJC data model structure and required fields
- EJC-specific hole rules and boundary values
- EJC validation service integration
- EJC API endpoints (/ejc/boxes)
- STEP parser dimension extraction
- EJC validate endpoint accepts EJC box IDs
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import (
    EJC_BOX_MODELS_DATA,
    EJC_MIN_EDGE_MARGIN,
    EJC_MIN_HOLE_CLEARANCE,
    EJC_MAX_HOLE_DIAMETER,
    get_all_ejc_box_models,
    get_ejc_box_model_by_id,
)
from app.schemas import EJCBoxModel, ConfigurationInput
from app.services.validation.validation_service import validate_hole_placement
from app.services.step_parser import extract_dimensions_from_step

client = TestClient(app)

VALID_EJC_CONFIG = {
    "box_id": "ejc03",
    "terminals": 5,
    "holes_top": 1,
    "holes_bottom": 1,
    "holes_left": 0,
    "holes_right": 0,
}


# ============================================================
# EJC data model tests
# ============================================================

class TestEJCBoxModelData:
    def test_ejc_models_defined(self):
        """EJC_BOX_MODELS_DATA must be non-empty."""
        assert len(EJC_BOX_MODELS_DATA) > 0

    def test_ejc_models_have_required_fields(self):
        """Every EJC model entry must contain all required schema keys."""
        required_keys = {
            "id", "name",
            "internal_length", "internal_width", "internal_depth",
            "mounting_plate_x", "mounting_plate_y",
            "max_holes_long", "max_holes_short",
            "rail_count", "max_terminals",
            "ip_rating", "has_earth_plate",
        }
        for entry in EJC_BOX_MODELS_DATA:
            assert required_keys.issubset(entry.keys()), (
                f"EJC model {entry.get('id')} is missing required keys"
            )

    def test_ejc_ids_start_with_ejc(self):
        """All EJC model IDs must start with 'ejc'."""
        for entry in EJC_BOX_MODELS_DATA:
            assert entry["id"].startswith("ejc"), (
                f"Model ID '{entry['id']}' does not start with 'ejc'"
            )

    def test_ejc_positive_dimensions(self):
        """All EJC models must have positive internal dimensions."""
        for entry in EJC_BOX_MODELS_DATA:
            assert entry["internal_length"] > 0
            assert entry["internal_width"] > 0
            assert entry["internal_depth"] > 0

    def test_ejc_ip_rating_format(self):
        """IP rating must follow IPxx format."""
        for entry in EJC_BOX_MODELS_DATA:
            assert entry["ip_rating"].startswith("IP"), (
                f"ip_rating '{entry['ip_rating']}' does not start with 'IP'"
            )

    def test_get_all_ejc_box_models_returns_ejc_instances(self):
        """get_all_ejc_box_models must return EJCBoxModel instances."""
        models = get_all_ejc_box_models()
        assert len(models) == len(EJC_BOX_MODELS_DATA)
        for model in models:
            assert isinstance(model, EJCBoxModel)

    def test_get_ejc_box_model_by_id_found(self):
        """get_ejc_box_model_by_id must return the correct model."""
        first_id = EJC_BOX_MODELS_DATA[0]["id"]
        model = get_ejc_box_model_by_id(first_id)
        assert model is not None
        assert model.id == first_id

    def test_get_ejc_box_model_by_id_not_found(self):
        """get_ejc_box_model_by_id must return None for unknown IDs."""
        assert get_ejc_box_model_by_id("ejc_unknown") is None


# ============================================================
# EJC schema tests
# ============================================================

class TestEJCBoxModelSchema:
    def test_ejc_schema_has_ip_rating(self):
        """EJCBoxModel must expose ip_rating field."""
        entry = EJC_BOX_MODELS_DATA[0]
        model = EJCBoxModel(**entry)
        assert hasattr(model, "ip_rating")
        assert model.ip_rating.startswith("IP")

    def test_ejc_schema_has_earth_plate_flag(self):
        """EJCBoxModel must expose has_earth_plate field."""
        entry = EJC_BOX_MODELS_DATA[0]
        model = EJCBoxModel(**entry)
        assert hasattr(model, "has_earth_plate")
        assert isinstance(model.has_earth_plate, bool)

    def test_ejc_schema_default_ip_rating(self):
        """EJCBoxModel ip_rating must default to 'IP66'."""
        model = EJCBoxModel(
            id="ejc_test",
            name="EJC Test",
            internal_length=100,
            internal_width=100,
            internal_depth=80,
            mounting_plate_x=110,
            mounting_plate_y=110,
            max_holes_long=2,
            max_holes_short=2,
            rail_count=1,
            max_terminals=10,
        )
        assert model.ip_rating == "IP66"

    def test_ejc_schema_default_earth_plate(self):
        """EJCBoxModel has_earth_plate must default to False."""
        model = EJCBoxModel(
            id="ejc_test",
            name="EJC Test",
            internal_length=100,
            internal_width=100,
            internal_depth=80,
            mounting_plate_x=110,
            mounting_plate_y=110,
            max_holes_long=2,
            max_holes_short=2,
            rail_count=1,
            max_terminals=10,
        )
        assert model.has_earth_plate is False


# ============================================================
# EJC hole rules and boundary constants tests
# ============================================================

class TestEJCHoleRules:
    def test_ejc_edge_margin_tighter_than_ejb(self):
        """EJC edge margin must be >= EJB edge margin (15mm)."""
        assert EJC_MIN_EDGE_MARGIN >= 15

    def test_ejc_hole_clearance_tighter_than_ejb(self):
        """EJC hole clearance must be >= EJB clearance (5mm)."""
        assert EJC_MIN_HOLE_CLEARANCE >= 5

    def test_ejc_max_hole_diameter_defined(self):
        """EJC max hole diameter must be positive."""
        assert EJC_MAX_HOLE_DIAMETER > 0

    def test_validate_hole_placement_ejc_tighter(self):
        """
        EJC hole placement must allow fewer holes than EJB
        for the same side length due to tighter tolerances.
        """
        side_length = 200.0
        _, _, max_ejb = validate_hole_placement(1, side_length, ejc=False)
        _, _, max_ejc = validate_hole_placement(1, side_length, ejc=True)
        assert max_ejc <= max_ejb, (
            "EJC should allow equal or fewer holes than EJB on the same side"
        )

    def test_validate_hole_placement_ejc_respects_edge_margin(self):
        """
        A very small side length should result in 0 max holes under EJC rules.
        """
        tiny_side = EJC_MIN_EDGE_MARGIN * 2  # no space for even one hole
        is_valid, _, max_possible = validate_hole_placement(1, tiny_side, ejc=True)
        assert not is_valid or max_possible == 0


# ============================================================
# EJC validation endpoint tests
# ============================================================

class TestEJCValidationEndpoint:
    def test_ejc_validate_valid_config(self):
        """A valid EJC configuration must return is_valid=True."""
        response = client.post("/api/v1/validate", json=VALID_EJC_CONFIG)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    def test_ejc_validate_too_many_terminals(self):
        """Exceeding EJC terminal capacity must produce a validation error."""
        config = {**VALID_EJC_CONFIG, "terminals": 9999}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        fields = [e["field"] for e in data["errors"]]
        assert "terminals" in fields

    def test_ejc_validate_too_many_holes(self):
        """Exceeding EJC hole capacity must produce a validation error."""
        config = {**VALID_EJC_CONFIG, "holes_top": 999}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False

    def test_ejc_validate_unknown_box_id(self):
        """Unknown EJC box ID must produce a validation error."""
        config = {**VALID_EJC_CONFIG, "box_id": "ejc_unknown"}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any(e["field"] == "box_id" for e in data["errors"])


# ============================================================
# EJC API endpoint tests
# ============================================================

class TestEJCBoxEndpoints:
    def test_list_ejc_boxes_returns_200(self):
        """GET /ejc/boxes must return 200."""
        response = client.get("/api/v1/ejc/boxes")
        assert response.status_code == 200

    def test_list_ejc_boxes_returns_all_models(self):
        """GET /ejc/boxes must return all defined EJC models."""
        response = client.get("/api/v1/ejc/boxes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(EJC_BOX_MODELS_DATA)

    def test_list_ejc_boxes_have_ejc_ids(self):
        """All models returned by GET /ejc/boxes must have IDs starting with 'ejc'."""
        response = client.get("/api/v1/ejc/boxes")
        assert response.status_code == 200
        for model in response.json():
            assert model["id"].startswith("ejc")

    def test_list_ejc_boxes_include_ip_rating(self):
        """Each EJC model response must include ip_rating."""
        response = client.get("/api/v1/ejc/boxes")
        assert response.status_code == 200
        for model in response.json():
            assert "ip_rating" in model

    def test_get_ejc_box_by_id_found(self):
        """GET /ejc/boxes/{id} must return the correct model."""
        box_id = EJC_BOX_MODELS_DATA[0]["id"]
        response = client.get(f"/api/v1/ejc/boxes/{box_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == box_id

    def test_get_ejc_box_by_id_not_found(self):
        """GET /ejc/boxes/{id} with unknown ID must return 404."""
        response = client.get("/api/v1/ejc/boxes/ejc_unknown")
        assert response.status_code == 404


# ============================================================
# STEP parser tests
# ============================================================

class TestSTEPParser:
    _MINIMAL_STEP = """
ISO-10303-21;
HEADER;
ENDSEC;
DATA;
#1 = CARTESIAN_POINT ( 'Origin', ( 0.0, 0.0, 0.0 ) );
#2 = CARTESIAN_POINT ( 'Corner', ( 200.0, 150.0, 100.0 ) );
#3 = CARTESIAN_POINT ( 'Mid', ( 100.0, 75.0, 50.0 ) );
ENDSEC;
END-ISO-10303-21;
"""

    def test_extract_returns_dict(self):
        """extract_dimensions_from_step must return a dict for valid STEP content."""
        result = extract_dimensions_from_step(self._MINIMAL_STEP)
        assert result is not None
        assert isinstance(result, dict)

    def test_extract_correct_length(self):
        """internal_length must equal max_x - min_x."""
        result = extract_dimensions_from_step(self._MINIMAL_STEP)
        assert result["internal_length"] == pytest.approx(200.0)

    def test_extract_correct_width(self):
        """internal_width must equal max_y - min_y."""
        result = extract_dimensions_from_step(self._MINIMAL_STEP)
        assert result["internal_width"] == pytest.approx(150.0)

    def test_extract_correct_depth(self):
        """internal_depth must equal max_z - min_z."""
        result = extract_dimensions_from_step(self._MINIMAL_STEP)
        assert result["internal_depth"] == pytest.approx(100.0)

    def test_extract_returns_none_for_empty(self):
        """extract_dimensions_from_step must return None when no points found."""
        result = extract_dimensions_from_step("ISO-10303-21;\nHEADER;\nENDSEC;\nDATA;\nENDSEC;\n")
        assert result is None

    def test_extract_handles_scientific_notation(self):
        """Parser must handle STEP coordinates in scientific notation."""
        step = """
DATA;
#1 = CARTESIAN_POINT ( 'A', ( 0.0E+0, 0.0E+0, 0.0E+0 ) );
#2 = CARTESIAN_POINT ( 'B', ( 3.0E+2, 2.0E+2, 8.0E+1 ) );
ENDSEC;
"""
        result = extract_dimensions_from_step(step)
        assert result is not None
        assert result["internal_length"] == pytest.approx(300.0)
        assert result["internal_width"] == pytest.approx(200.0)
        assert result["internal_depth"] == pytest.approx(80.0)

    def test_extract_keys_present(self):
        """Result dict must contain the three dimension keys."""
        result = extract_dimensions_from_step(self._MINIMAL_STEP)
        assert set(result.keys()) == {"internal_length", "internal_width", "internal_depth"}
