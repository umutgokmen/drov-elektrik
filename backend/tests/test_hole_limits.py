"""
Test hole placement limits for all 9 EJB variants and all hole sizes.
"""
import pytest
from app.models import get_box_model_by_id, HOLE_SIZES
from app.services.validation.validation_service import validate_hole_placement, run_full_validation
from tests.conftest import make_config


HOLE_SIZE_IDS = list(HOLE_SIZES.keys())


class TestHolePlacementPerModel:
    """Verify max hole calculations per box model and side"""

    @pytest.fixture(params=[
        "ejb21", "ejb31", "ejb51", "ejb61", "ejb63",
        "ejb71", "ejb73", "ejb91", "ejb93",
    ])
    def box(self, request):
        return get_box_model_by_id(request.param)

    def test_zero_holes_always_valid(self, box):
        is_valid, msg, _ = validate_hole_placement(0, box.internal_width)
        assert is_valid
        assert msg == ""

    def test_one_hole_always_valid(self, box):
        is_valid, _, _ = validate_hole_placement(1, box.internal_width, "M20")
        assert is_valid

    def test_exceeding_short_side_m20(self, box):
        """Requesting more holes than physically possible must fail"""
        is_valid, msg, max_possible = validate_hole_placement(
            999, box.internal_width, "M20"
        )
        assert not is_valid
        assert max_possible > 0
        assert max_possible < 999

    def test_exceeding_long_side_m20(self, box):
        is_valid, msg, max_possible = validate_hole_placement(
            999, box.internal_length, "M20"
        )
        assert not is_valid
        assert max_possible > 0

    @pytest.mark.parametrize("hole_size", HOLE_SIZE_IDS)
    def test_max_possible_is_consistent(self, box, hole_size):
        """max_possible must be the same regardless of request count"""
        _, _, max_at_1000 = validate_hole_placement(1000, box.internal_width, hole_size)
        _, _, max_at_500 = validate_hole_placement(500, box.internal_width, hole_size)
        assert max_at_1000 == max_at_500

    @pytest.mark.parametrize("hole_size", HOLE_SIZE_IDS)
    def test_max_possible_fits(self, box, hole_size):
        """Requesting exactly max_possible must be valid"""
        _, _, max_possible = validate_hole_placement(999, box.internal_width, hole_size)
        if max_possible > 0:
            is_valid, _, _ = validate_hole_placement(max_possible, box.internal_width, hole_size)
            assert is_valid

    @pytest.mark.parametrize("hole_size", HOLE_SIZE_IDS)
    def test_max_plus_one_fails(self, box, hole_size):
        """Requesting max_possible + 1 must fail"""
        _, _, max_possible = validate_hole_placement(999, box.internal_width, hole_size)
        is_valid, _, _ = validate_hole_placement(max_possible + 1, box.internal_width, hole_size)
        assert not is_valid

    def test_larger_holes_have_smaller_max(self, box):
        """M50 should allow fewer holes than M20 on the same side"""
        _, _, max_m20 = validate_hole_placement(999, box.internal_width, "M20")
        _, _, max_m50 = validate_hole_placement(999, box.internal_width, "M50")
        assert max_m50 <= max_m20


class TestHoleValidationViaFullValidation:
    """Test hole validation through the full validation pipeline"""

    def test_valid_config_with_holes_all_sides(self):
        config = make_config("ejb61", holes_top=2, holes_bottom=2, holes_left=2, holes_right=2)
        result = run_full_validation(config)
        assert result.is_valid

    def test_too_many_holes_top_returns_error(self):
        config = make_config("ejb21", holes_top=999)
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "holes_top" in fields

    def test_too_many_holes_bottom_returns_error(self):
        config = make_config("ejb21", holes_bottom=999)
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "holes_bottom" in fields

    def test_too_many_holes_left_returns_error(self):
        config = make_config("ejb21", holes_left=999)
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "holes_left" in fields

    def test_too_many_holes_right_returns_error(self):
        config = make_config("ejb21", holes_right=999)
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "holes_right" in fields

    def test_holes_with_spec_m50(self):
        """Using HoleSideInput spec with M50 should apply larger clearance"""
        from app.schemas import HoleSideInput
        config = make_config(
            "ejb21",
            holes_top_spec=HoleSideInput(count=2, size="M50"),
        )
        result = run_full_validation(config)
        assert result.is_valid

    def test_holes_spec_overrides_legacy(self):
        """When spec is provided, legacy count should be synced"""
        from app.schemas import HoleSideInput
        config = make_config(
            "ejb31",
            holes_top=0,
            holes_top_spec=HoleSideInput(count=3, size="M25"),
        )
        assert config.holes_top == 3
