"""
Test cover element validation: collision and boundary checks.
"""
import pytest
from app.schemas import CoverElementPlacement
from app.services.validation.cover_validation import validate_cover_elements


class TestCoverElementBoundary:
    """Test cover element boundary validation"""

    def test_centered_element_valid(self):
        placements = [CoverElementPlacement(element_id="btn-22-green", x=100, y=100)]
        errors, warnings = validate_cover_elements(placements, "ejb61")
        assert len(errors) == 0

    def test_element_too_close_to_left_edge(self):
        placements = [CoverElementPlacement(element_id="btn-22-green", x=5, y=100)]
        errors, _ = validate_cover_elements(placements, "ejb61")
        assert len(errors) > 0

    def test_element_too_close_to_top_edge(self):
        placements = [CoverElementPlacement(element_id="btn-22-green", x=100, y=5)]
        errors, _ = validate_cover_elements(placements, "ejb61")
        assert len(errors) > 0

    def test_element_too_close_to_right_edge(self):
        placements = [CoverElementPlacement(element_id="btn-22-green", x=555, y=100)]
        errors, _ = validate_cover_elements(placements, "ejb61")
        assert len(errors) > 0

    def test_element_too_close_to_bottom_edge(self):
        placements = [CoverElementPlacement(element_id="btn-22-green", x=100, y=355)]
        errors, _ = validate_cover_elements(placements, "ejb61")
        assert len(errors) > 0

    def test_unknown_element_id(self):
        placements = [CoverElementPlacement(element_id="nonexistent", x=100, y=100)]
        errors, _ = validate_cover_elements(placements, "ejb61")
        assert len(errors) > 0
        assert "Bilinmeyen" in errors[0].message

    def test_empty_placements_valid(self):
        errors, warnings = validate_cover_elements([], "ejb61")
        assert len(errors) == 0
        assert len(warnings) == 0


class TestCoverElementCollision:
    """Test cover element collision detection"""

    def test_overlapping_elements(self):
        placements = [
            CoverElementPlacement(element_id="btn-22-green", x=100, y=100),
            CoverElementPlacement(element_id="btn-22-red", x=105, y=100),
        ]
        errors, _ = validate_cover_elements(placements, "ejb61")
        collision_errors = [e for e in errors if "cakisiyor" in e.message]
        assert len(collision_errors) > 0

    def test_close_but_not_overlapping(self):
        """Elements close together should produce a warning"""
        placements = [
            CoverElementPlacement(element_id="btn-22-green", x=100, y=100),
            CoverElementPlacement(element_id="btn-22-red", x=135, y=100),
        ]
        _, warnings = validate_cover_elements(placements, "ejb61")
        assert len(warnings) > 0

    def test_well_spaced_elements_no_warnings(self):
        placements = [
            CoverElementPlacement(element_id="btn-22-green", x=100, y=100),
            CoverElementPlacement(element_id="btn-22-red", x=200, y=100),
        ]
        errors, warnings = validate_cover_elements(placements, "ejb61")
        assert len(errors) == 0
        assert len(warnings) == 0

    def test_three_elements_pairwise_check(self):
        """Collision check should be pairwise for all elements"""
        placements = [
            CoverElementPlacement(element_id="btn-22-green", x=100, y=100),
            CoverElementPlacement(element_id="btn-22-red", x=200, y=100),
            CoverElementPlacement(element_id="btn-22-yellow", x=105, y=100),
        ]
        errors, _ = validate_cover_elements(placements, "ejb61")
        collision_errors = [e for e in errors if "cakisiyor" in e.message]
        assert len(collision_errors) > 0

    def test_emergency_stop_larger_bezel(self):
        """Emergency stop has 40mm bezel, needs more space"""
        placements = [
            CoverElementPlacement(element_id="estop-40", x=100, y=100),
            CoverElementPlacement(element_id="btn-22-green", x=130, y=100),
        ]
        errors, _ = validate_cover_elements(placements, "ejb61")
        assert len(errors) > 0 or any("dar" in w.message for w in validate_cover_elements(placements, "ejb61")[1])
