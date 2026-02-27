"""
Test terminal capacity validation for all 9 EJB variants.
"""
import pytest
from app.models import get_box_model_by_id
from app.services.validation.validation_service import validate_terminal_placement, run_full_validation
from app.services.geometry_service import calculate_rail_layout
from tests.conftest import make_config


BOX_IDS = ["ejb21", "ejb31", "ejb51", "ejb61", "ejb63", "ejb71", "ejb73", "ejb91", "ejb93"]


class TestTerminalCapacityPerModel:
    """Verify terminal limits per box model"""

    @pytest.fixture(params=BOX_IDS)
    def box(self, request):
        return get_box_model_by_id(request.param)

    def test_zero_terminals_valid(self, box):
        is_valid, msg, _ = validate_terminal_placement(0, box)
        assert is_valid

    def test_max_terminals_valid(self, box):
        is_valid, msg, _ = validate_terminal_placement(box.max_terminals, box)
        assert is_valid

    def test_exceeding_max_terminals_fails(self, box):
        is_valid, msg, max_possible = validate_terminal_placement(box.max_terminals + 1, box)
        assert not is_valid
        assert max_possible <= box.max_terminals

    def test_physical_rail_limit_consistent(self, box):
        """Physical rail limit (width / terminal_width) * rail_count >= max_terminals"""
        from app.services.validation.validation_service import TERMINAL_WIDTH, RAIL_MARGIN
        available = box.internal_width - 2 * RAIL_MARGIN
        physical_max = int(available / TERMINAL_WIDTH) * box.rail_count
        assert physical_max >= box.max_terminals

    def test_one_terminal_valid(self, box):
        is_valid, _, _ = validate_terminal_placement(1, box)
        assert is_valid


class TestTerminalLayoutDistribution:
    """Verify terminals are distributed across rails correctly"""

    @pytest.fixture(params=BOX_IDS)
    def box(self, request):
        return get_box_model_by_id(request.param)

    def test_terminals_distributed_evenly(self, box):
        count = box.max_terminals
        rails = calculate_rail_layout(box, count)
        total = sum(r.terminal_count for r in rails)
        assert total == count

    def test_zero_terminals_all_rails_empty(self, box):
        rails = calculate_rail_layout(box, 0)
        assert all(r.terminal_count == 0 for r in rails)

    def test_rail_count_matches_box(self, box):
        rails = calculate_rail_layout(box, 10)
        assert len(rails) == box.rail_count

    def test_rail_width_positive(self, box):
        rails = calculate_rail_layout(box, 1)
        for rail in rails:
            assert rail.width > 0

    def test_no_negative_terminal_count(self, box):
        rails = calculate_rail_layout(box, 1)
        for rail in rails:
            assert rail.terminal_count >= 0


class TestTerminalValidationViaFullValidation:
    """Test terminal validation through the full pipeline"""

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_max_terminals_pass(self, box_id):
        box = get_box_model_by_id(box_id)
        config = make_config(box_id, terminals=box.max_terminals)
        result = run_full_validation(config)
        assert result.is_valid

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_exceeding_terminals_fail(self, box_id):
        box = get_box_model_by_id(box_id)
        config = make_config(box_id, terminals=box.max_terminals + 1)
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "terminals" in fields

    def test_90_percent_capacity_warning(self):
        """Approaching capacity should trigger a warning"""
        box = get_box_model_by_id("ejb91")
        threshold = int(box.max_terminals * 0.91)
        config = make_config("ejb91", terminals=threshold)
        result = run_full_validation(config)
        assert result.is_valid
        warning_fields = [w.field for w in result.warnings]
        assert "terminals" in warning_fields
