"""
Test geometry/layout calculations for all EJB variants.
"""
import pytest
from app.models import get_box_model_by_id
from app.services.geometry_service import (
    calculate_hole_positions,
    calculate_rail_layout,
    calculate_full_layout,
    MIN_EDGE_MARGIN,
)
from tests.conftest import make_config


BOX_IDS = ["ejb21", "ejb31", "ejb51", "ejb61", "ejb63", "ejb71", "ejb73", "ejb91", "ejb93"]


class TestHolePositionCalculations:
    """Verify hole positions respect edge margins and spacing"""

    def test_zero_count_returns_empty(self):
        result = calculate_hole_positions(0, 200)
        assert result == []

    def test_single_hole_centered(self):
        positions = calculate_hole_positions(1, 200)
        assert len(positions) == 1
        assert positions[0].position == pytest.approx(100, abs=1)

    def test_positions_within_bounds(self):
        for count in [1, 2, 3, 5, 10]:
            positions = calculate_hole_positions(count, 500)
            for p in positions:
                assert p.position >= MIN_EDGE_MARGIN
                assert p.position <= 500 - MIN_EDGE_MARGIN

    def test_positions_evenly_spaced(self):
        positions = calculate_hole_positions(4, 400)
        spacings = [positions[i+1].position - positions[i].position for i in range(len(positions)-1)]
        for s in spacings:
            assert s == pytest.approx(spacings[0], abs=0.01)

    def test_count_matches_request(self):
        for count in [1, 3, 7, 15]:
            positions = calculate_hole_positions(count, 1000)
            assert len(positions) == count


class TestFullLayoutCalculation:
    """Test full layout output per box model"""

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_layout_returns_correct_rail_count(self, box_id):
        box = get_box_model_by_id(box_id)
        config = make_config(box_id, terminals=10, holes_top=2, holes_bottom=2)
        layout = calculate_full_layout(config)
        assert len(layout.rails) == box.rail_count

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_layout_hole_counts_match(self, box_id):
        config = make_config(box_id, terminals=0, holes_top=3, holes_bottom=2, holes_left=1, holes_right=4)
        layout = calculate_full_layout(config)
        assert len(layout.holes_top) == 3
        assert len(layout.holes_bottom) == 2
        assert len(layout.holes_left) == 1
        assert len(layout.holes_right) == 4

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_layout_zero_holes(self, box_id):
        config = make_config(box_id, terminals=5)
        layout = calculate_full_layout(config)
        assert len(layout.holes_top) == 0
        assert len(layout.holes_bottom) == 0
        assert len(layout.holes_left) == 0
        assert len(layout.holes_right) == 0

    def test_invalid_box_raises(self):
        config = make_config("invalid_box")
        with pytest.raises(ValueError):
            calculate_full_layout(config)

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_hole_xy_coordinates_set(self, box_id):
        config = make_config(box_id, holes_top=1, holes_bottom=1, holes_left=1, holes_right=1)
        layout = calculate_full_layout(config)
        for h in layout.holes_top:
            assert h.x is not None
            assert h.y is not None and h.y < 0
        for h in layout.holes_bottom:
            assert h.x is not None
            assert h.y is not None and h.y > 0
        for h in layout.holes_left:
            assert h.x is not None and h.x < 0
            assert h.y is not None
        for h in layout.holes_right:
            assert h.x is not None and h.x > 0
            assert h.y is not None
