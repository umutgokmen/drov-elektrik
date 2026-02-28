"""
Tests for ESP box type integration (issue #23)
"""
import pytest
from app.models import get_all_box_models, get_box_model_by_id, get_hole_rules, ESP_HOLE_RULES, EJB_HOLE_RULES
from app.schemas import ConfigurationInput
# Import directly to avoid the drawing engine dependency (requires matplotlib)
from app.services.validation.validation_service import (
    validate_hole_placement,
    validate_terminal_placement,
    run_full_validation,
)


# --- ESP data model tests ---

class TestESPModels:
    def test_esp_models_exist(self):
        all_models = get_all_box_models()
        esp_ids = [m.id for m in all_models if m.id.startswith("esp")]
        assert len(esp_ids) >= 1, "At least one ESP model must be present"

    def test_esp1_lookup(self):
        box = get_box_model_by_id("esp1")
        assert box is not None
        assert box.name == "ESP 1"
        assert box.internal_length > 0
        assert box.internal_width > 0
        assert box.internal_depth > 0
        assert box.max_terminals >= 0
        assert box.rail_count >= 1

    def test_esp2_lookup(self):
        box = get_box_model_by_id("esp2")
        assert box is not None
        assert box.max_terminals > 0

    def test_esp3_lookup(self):
        box = get_box_model_by_id("esp3")
        assert box is not None

    def test_esp4_lookup(self):
        box = get_box_model_by_id("esp4")
        assert box is not None

    def test_esp5_lookup(self):
        box = get_box_model_by_id("esp5")
        assert box is not None

    def test_esp_max_holes_positive(self):
        for esp_id in ("esp1", "esp2", "esp3", "esp4", "esp5"):
            box = get_box_model_by_id(esp_id)
            assert box.max_holes_long >= 0
            assert box.max_holes_short >= 0

    def test_esp_mounting_plate_defined(self):
        box = get_box_model_by_id("esp1")
        assert box.mounting_plate_x > 0
        assert box.mounting_plate_y > 0

    def test_unknown_esp_returns_none(self):
        assert get_box_model_by_id("esp99") is None


# --- Hole rules tests ---

class TestHoleRules:
    def test_esp_hole_rules_returned(self):
        rules = get_hole_rules("esp1")
        assert rules == ESP_HOLE_RULES

    def test_ejb_hole_rules_returned(self):
        rules = get_hole_rules("ejb21")
        assert rules == EJB_HOLE_RULES

    def test_esp_edge_margin_smaller_than_ejb(self):
        assert ESP_HOLE_RULES["min_edge_margin"] < EJB_HOLE_RULES["min_edge_margin"]

    def test_esp_hole_diameter_is_m20(self):
        assert ESP_HOLE_RULES["hole_diameter"] == 20

    def test_ejb_hole_diameter_is_m20(self):
        assert EJB_HOLE_RULES["hole_diameter"] == 20


# --- Validation with ESP box_id ---

class TestESPHolePlacement:
    def test_zero_holes_always_valid(self):
        is_valid, _, _ = validate_hole_placement(0, 80, "esp1")
        assert is_valid

    def test_within_limit_valid(self):
        box = get_box_model_by_id("esp1")
        is_valid, _, _ = validate_hole_placement(
            box.max_holes_short, box.internal_width, "esp1"
        )
        assert is_valid

    def test_exceeds_physical_limit_invalid(self):
        box = get_box_model_by_id("esp1")
        # Request far more holes than can physically fit
        is_valid, msg, max_p = validate_hole_placement(999, box.internal_width, "esp1")
        assert not is_valid
        assert max_p < 999

    def test_esp_allows_more_holes_than_ejb_for_same_width(self):
        """ESP's smaller edge margin should allow at least as many holes as EJB
        on the same side length."""
        side = 150
        _, _, max_esp = validate_hole_placement(1, side, "esp1")
        _, _, max_ejb = validate_hole_placement(1, side, "ejb21")
        assert max_esp >= max_ejb


# --- Full validation with ESP config ---

class TestESPFullValidation:
    def _make_config(self, box_id, terminals=0, **holes):
        return ConfigurationInput(
            box_id=box_id,
            terminals=terminals,
            holes_top=holes.get("holes_top", 0),
            holes_bottom=holes.get("holes_bottom", 0),
            holes_left=holes.get("holes_left", 0),
            holes_right=holes.get("holes_right", 0),
        )

    def test_empty_esp1_config_valid(self):
        config = self._make_config("esp1")
        result = run_full_validation(config)
        assert result.is_valid
        assert result.errors == []

    def test_esp1_max_terminals_valid(self):
        box = get_box_model_by_id("esp1")
        config = self._make_config("esp1", terminals=box.max_terminals)
        result = run_full_validation(config)
        assert result.is_valid

    def test_esp1_over_terminals_invalid(self):
        config = self._make_config("esp1", terminals=9999)
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "terminals" in fields

    def test_esp3_valid_with_holes(self):
        config = self._make_config("esp3", holes_top=2, holes_bottom=2)
        result = run_full_validation(config)
        assert result.is_valid

    def test_invalid_esp_id_returns_error(self):
        config = self._make_config("esp99")
        result = run_full_validation(config)
        assert not result.is_valid
        assert any(e.field == "box_id" for e in result.errors)
