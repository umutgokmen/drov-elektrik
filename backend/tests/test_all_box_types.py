"""
Tests for issue #28 - Validation & tests for all box types.

Covers:
- ESP validation tests (holes, terminals, valid config, over-limit)
- ESA validation tests
- ESX validation tests
- EJBX validation tests
- EJC validation tests
- Cross-model comparison tests
- PDF/STEP/DXF output validation (all types)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import get_box_model_by_id, get_all_box_models, get_ejc_box_model_by_id

client = TestClient(app)

# Representative one model per series for focused API tests
ESP_CONFIG = {
    "box_id": "esp1",
    "terminals": 5,
    "holes_top": 2,
    "holes_bottom": 2,
    "holes_left": 0,
    "holes_right": 0,
}

ESA_CONFIG = {
    "box_id": "esa1",
    "terminals": 10,
    "holes_top": 3,
    "holes_bottom": 3,
    "holes_left": 1,
    "holes_right": 1,
}

ESX_CONFIG = {
    "box_id": "esx1",
    "terminals": 15,
    "holes_top": 4,
    "holes_bottom": 4,
    "holes_left": 2,
    "holes_right": 2,
}

EJBX_CONFIG = {
    "box_id": "ejbx1",
    "terminals": 15,
    "holes_top": 2,
    "holes_bottom": 2,
    "holes_left": 1,
    "holes_right": 1,
}

EJC_CONFIG = {
    "box_id": "ejc01",
    "terminals": 8,
    "holes_top": 2,
    "holes_bottom": 2,
    "holes_left": 1,
    "holes_right": 1,
}

ALL_SERIES_CONFIGS = [ESP_CONFIG, ESA_CONFIG, ESX_CONFIG, EJBX_CONFIG]

ALL_BOX_IDS = [
    "esp1", "esp2",
    "esa1", "esa2",
    "esx1", "esx2",
    "ejbx1", "ejbx2",
]

# Consecutive pairs within each series: (smaller_variant, larger_variant)
SERIES_PAIRS = [
    (ALL_BOX_IDS[i], ALL_BOX_IDS[i + 1])
    for i in range(0, len(ALL_BOX_IDS), 2)
]


# ============================================================
# Box model data tests (all new series)
# ============================================================

class TestAllBoxModelsData:
    def test_all_new_box_ids_exist(self):
        """Every new box type must be retrievable by ID."""
        for box_id in ALL_BOX_IDS:
            box = get_box_model_by_id(box_id)
            assert box is not None, f"Box model '{box_id}' is missing from BOX_MODELS_DATA"

    def test_all_boxes_have_positive_dimensions(self):
        """All box models must have positive internal dimensions."""
        for box_id in ALL_BOX_IDS:
            box = get_box_model_by_id(box_id)
            assert box.internal_length > 0
            assert box.internal_width > 0
            assert box.internal_depth > 0

    def test_all_boxes_have_at_least_one_rail(self):
        """All box models must have at least one DIN rail."""
        for box_id in ALL_BOX_IDS:
            box = get_box_model_by_id(box_id)
            assert box.rail_count >= 1, f"{box_id}: rail_count must be >= 1"

    def test_all_boxes_have_positive_terminal_limit(self):
        """All box models must allow at least 1 terminal."""
        for box_id in ALL_BOX_IDS:
            box = get_box_model_by_id(box_id)
            assert box.max_terminals > 0, f"{box_id}: max_terminals must be > 0"

    def test_all_boxes_listed_in_api(self):
        """/api/v1/boxes must include all new box models."""
        response = client.get("/api/v1/boxes")
        assert response.status_code == 200
        returned_ids = {b["id"] for b in response.json()}
        for box_id in ALL_BOX_IDS:
            assert box_id in returned_ids, f"{box_id} not returned by /api/v1/boxes"

    def test_total_box_count_includes_new_types(self):
        """get_all_box_models must include EJB + all new series.

        9 existing EJB models + 10 new models (2 per new series) = 19 total.
        """
        all_models = get_all_box_models()
        assert len(all_models) >= 19


# ============================================================
# ESP validation tests
# ============================================================

class TestESPValidation:
    def test_esp_valid_config_passes(self):
        response = client.post("/api/v1/validate", json=ESP_CONFIG)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_esp_too_many_terminals_fails(self):
        box = get_box_model_by_id("esp1")
        config = {**ESP_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_esp_too_many_holes_top_fails(self):
        box = get_box_model_by_id("esp1")
        config = {**ESP_CONFIG, "holes_top": box.max_holes_long + 10}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_esp_zero_terminals_passes(self):
        config = {**ESP_CONFIG, "terminals": 0}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_esp_zero_holes_passes(self):
        config = {**ESP_CONFIG, "holes_top": 0, "holes_bottom": 0,
                  "holes_left": 0, "holes_right": 0}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_esp2_valid_config_passes(self):
        config = {**ESP_CONFIG, "box_id": "esp2", "terminals": 10}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True


# ============================================================
# ESA validation tests
# ============================================================

class TestESAValidation:
    def test_esa_valid_config_passes(self):
        response = client.post("/api/v1/validate", json=ESA_CONFIG)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_esa_too_many_terminals_fails(self):
        box = get_box_model_by_id("esa1")
        config = {**ESA_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_esa_too_many_holes_bottom_fails(self):
        box = get_box_model_by_id("esa1")
        config = {**ESA_CONFIG, "holes_bottom": box.max_holes_long + 10}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_esa_error_includes_field_name(self):
        box = get_box_model_by_id("esa1")
        config = {**ESA_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        data = response.json()
        assert any(e["field"] == "terminals" for e in data["errors"])

    def test_esa2_valid_config_passes(self):
        config = {**ESA_CONFIG, "box_id": "esa2", "terminals": 20}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True


# ============================================================
# ESX validation tests
# ============================================================

class TestESXValidation:
    def test_esx_valid_config_passes(self):
        response = client.post("/api/v1/validate", json=ESX_CONFIG)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_esx_too_many_terminals_fails(self):
        box = get_box_model_by_id("esx1")
        config = {**ESX_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_esx_too_many_holes_left_fails(self):
        box = get_box_model_by_id("esx1")
        config = {**ESX_CONFIG, "holes_left": box.max_holes_short + 10}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_esx_max_terminals_exact_passes(self):
        box = get_box_model_by_id("esx1")
        config = {**ESX_CONFIG, "terminals": box.max_terminals}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_esx2_valid_config_passes(self):
        config = {**ESX_CONFIG, "box_id": "esx2", "terminals": 30}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True


# ============================================================
# EJBX validation tests
# ============================================================

class TestEJBXValidation:
    def test_ejbx_valid_config_passes(self):
        response = client.post("/api/v1/validate", json=EJBX_CONFIG)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_ejbx_too_many_terminals_fails(self):
        box = get_box_model_by_id("ejbx1")
        config = {**EJBX_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_ejbx_too_many_holes_right_fails(self):
        box = get_box_model_by_id("ejbx1")
        config = {**EJBX_CONFIG, "holes_right": box.max_holes_short + 10}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_ejbx_error_has_max_possible(self):
        box = get_box_model_by_id("ejbx1")
        config = {**EJBX_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        data = response.json()
        terminal_errors = [e for e in data["errors"] if e["field"] == "terminals"]
        assert len(terminal_errors) == 1
        assert terminal_errors[0]["max_possible"] is not None

    def test_ejbx2_valid_config_passes(self):
        config = {**EJBX_CONFIG, "box_id": "ejbx2", "terminals": 40}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True


# ============================================================
# EJC validation tests
# ============================================================

class TestEJCValidation:
    def test_ejc_valid_config_passes(self):
        response = client.post("/api/v1/validate", json=EJC_CONFIG)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_ejc_too_many_terminals_fails(self):
        box = get_ejc_box_model_by_id("ejc01")
        config = {**EJC_CONFIG, "terminals": box.max_terminals + 1}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_ejc_too_many_holes_top_fails(self):
        box = get_ejc_box_model_by_id("ejc01")
        config = {**EJC_CONFIG, "holes_top": box.max_holes_long + 10}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_ejc_all_sides_with_holes_passes(self):
        config = {**EJC_CONFIG, "holes_top": 1, "holes_bottom": 1,
                  "holes_left": 1, "holes_right": 1}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True

    def test_ejc2_valid_config_passes(self):
        config = {**EJC_CONFIG, "box_id": "ejc02", "terminals": 15}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is True


# ============================================================
# Cross-model comparison tests
# ============================================================

class TestCrossModelComparison:
    def test_larger_series_has_more_terminals(self):
        """ESX should allow more terminals than ESP (larger enclosure)."""
        esp = get_box_model_by_id("esp1")
        esx = get_box_model_by_id("esx1")
        assert esx.max_terminals > esp.max_terminals

    def test_larger_series_has_more_holes(self):
        """ESX should allow more holes per side than ESP."""
        esp = get_box_model_by_id("esp1")
        esx = get_box_model_by_id("esx1")
        assert esx.max_holes_long >= esp.max_holes_long

    def test_ejbx_more_terminals_than_esp(self):
        """EJBX should accommodate more terminals than ESP."""
        esp = get_box_model_by_id("esp1")
        ejbx = get_box_model_by_id("ejbx1")
        assert ejbx.max_terminals > esp.max_terminals

    def test_second_variant_bigger_than_first(self):
        """Second model in each series must have >= terminals than first."""
        for first, second in SERIES_PAIRS:
            m1 = get_box_model_by_id(first)
            m2 = get_box_model_by_id(second)
            assert m2.max_terminals >= m1.max_terminals, (
                f"{second}.max_terminals must be >= {first}.max_terminals"
            )

    def test_invalid_box_id_returns_error(self):
        """Validation endpoint must return error for unknown box type."""
        config = {**ESP_CONFIG, "box_id": "unknown_type_xyz"}
        response = client.post("/api/v1/validate", json=config)
        assert response.status_code == 200
        assert response.json()["is_valid"] is False

    def test_all_series_valid_configs_pass_validation(self):
        """Each representative series config must pass validation."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/validate", json=config)
            assert response.status_code == 200, f"Unexpected status for {config['box_id']}"
            assert response.json()["is_valid"] is True, (
                f"Valid config for {config['box_id']} failed: {response.json()['errors']}"
            )

    def test_all_series_bom_endpoint_returns_200(self):
        """BOM endpoint must return 200 for each series representative."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/bom", json=config)
            assert response.status_code == 200, f"BOM failed for {config['box_id']}"

    def test_all_series_bom_includes_salt_malzeme(self):
        """BOM for each box type must include salt malzeme items."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/bom", json=config)
            assert response.status_code == 200
            data = response.json()
            salt_items = [i for i in data["items"] if i["is_salt_malzeme"]]
            assert len(salt_items) > 0, f"No salt malzeme in BOM for {config['box_id']}"


# ============================================================
# PDF/STEP/DXF output validation (all types)
# ============================================================

class TestOutputGenerationAllTypes:
    def test_dxf_returns_content_for_all_series(self):
        """DXF endpoint must return non-empty content for each series."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/generate/dxf", json=config)
            assert response.status_code == 200, (
                f"DXF failed for {config['box_id']}: {response.text}"
            )
            assert len(response.content) > 0

    def test_dxf_filename_contains_box_id_for_all_series(self):
        """DXF Content-Disposition must reference the box id for each series."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/generate/dxf", json=config)
            assert response.status_code == 200
            disposition = response.headers.get("content-disposition", "")
            assert config["box_id"].upper() in disposition.upper(), (
                f"Box id missing from DXF filename for {config['box_id']}"
            )

    def test_step_endpoint_registered_for_all_series(self):
        """STEP endpoint must be registered (not 404) for each series config."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/generate/step", json=config)
            assert response.status_code != 404, (
                f"/api/v1/generate/step returned 404 for {config['box_id']}"
            )

    def test_step_invalid_config_rejected_for_all_series(self):
        """Over-limit terminal count must be rejected before STEP generation."""
        for config in ALL_SERIES_CONFIGS:
            box = get_box_model_by_id(config["box_id"])
            bad_config = {**config, "terminals": box.max_terminals + 999}
            response = client.post("/api/v1/generate/step", json=bad_config)
            assert response.status_code == 400, (
                f"Expected 400 for over-limit terminals on {config['box_id']}, "
                f"got {response.status_code}"
            )

    def test_pdf_endpoint_registered_for_all_series(self):
        """PDF endpoint must be registered (not 404) for each series config."""
        for config in ALL_SERIES_CONFIGS:
            response = client.post("/api/v1/generate/pdf", json=config)
            assert response.status_code != 404, (
                f"/api/v1/generate/pdf returned 404 for {config['box_id']}"
            )
