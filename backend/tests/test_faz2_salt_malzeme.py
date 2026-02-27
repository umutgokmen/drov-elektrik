"""
Issue #22 - Faz 2 test & approval

Automation tests for salt malzeme (terminals-only) panel configurations
and output tests with different material combinations.
"""
import pytest
from app.services.validation.validation_service import run_full_validation
from app.services.geometry_service import calculate_full_layout
from app.schemas import ConfigurationInput


# ================================================================
# Salt malzeme (pure material - no holes) automation tests
# ================================================================

class TestSaltMalzemeValidation:
    """Validates that pure-material (holes=0) configurations pass engineering rules."""

    @pytest.mark.parametrize("box_id,terminals", [
        ("ejb21", 0),
        ("ejb21", 15),
        ("ejb21", 26),
        ("ejb31", 0),
        ("ejb31", 26),
        ("ejb31", 52),
        ("ejb51", 0),
        ("ejb51", 40),
        ("ejb51", 80),
        ("ejb61", 46),
        ("ejb71", 55),
        ("ejb91", 70),
    ])
    def test_salt_malzeme_is_valid(self, box_id, terminals):
        """Salt malzeme configs (no holes) must pass validation for all box models."""
        config = ConfigurationInput(
            box_id=box_id,
            terminals=terminals,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert result.is_valid, (
            f"Expected valid for {box_id} with {terminals} terminals, "
            f"got errors: {result.errors}"
        )
        assert result.errors == []

    def test_salt_malzeme_zero_terminals_valid(self):
        """A completely empty salt malzeme config (0 terminals, 0 holes) must be valid."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=0,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert result.is_valid
        assert result.errors == []

    def test_salt_malzeme_over_capacity_fails(self):
        """Exceeding terminal capacity in a salt malzeme config must fail validation."""
        config = ConfigurationInput(
            box_id="ejb21",
            terminals=999,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        fields = [e.field for e in result.errors]
        assert "terminals" in fields

    def test_salt_malzeme_at_90_percent_capacity_warns(self):
        """Salt malzeme at >=90% terminal capacity must trigger a warning."""
        # EJB 51 max_terminals=80, 90% = 72; physical rail max = 132, so 73 is valid but warns
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=73,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert result.is_valid
        warning_fields = [w.field for w in result.warnings]
        assert "terminals" in warning_fields

    def test_invalid_box_id_fails(self):
        """An unknown box_id must fail validation."""
        config = ConfigurationInput(
            box_id="ejb_unknown",
            terminals=10,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        assert any(e.field == "box_id" for e in result.errors)


class TestSaltMalzemeLayout:
    """Verifies geometry output for salt malzeme configurations."""

    @pytest.mark.parametrize("box_id,terminals", [
        ("ejb21", 10),
        ("ejb31", 20),
        ("ejb51", 40),
        ("ejb61", 46),
        ("ejb71", 55),
        ("ejb91", 70),
    ])
    def test_salt_malzeme_layout_rails_present(self, box_id, terminals):
        """Layout must contain rails for every box model in salt malzeme mode."""
        config = ConfigurationInput(
            box_id=box_id,
            terminals=terminals,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        layout = calculate_full_layout(config)
        assert len(layout.rails) > 0

    def test_salt_malzeme_no_holes_in_layout(self):
        """Salt malzeme layout must have no hole entries."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=24,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        layout = calculate_full_layout(config)
        assert layout.holes_top == []
        assert layout.holes_bottom == []
        assert layout.holes_left == []
        assert layout.holes_right == []

    def test_salt_malzeme_terminal_count_distributed_across_rails(self):
        """Total terminal count across all rails must equal configured terminal count."""
        terminals = 40
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=terminals,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        layout = calculate_full_layout(config)
        total_on_rails = sum(rail.terminal_count for rail in layout.rails)
        assert total_on_rails == terminals

    def test_salt_malzeme_zero_terminals_rails_present_but_empty(self):
        """With 0 terminals, rails must still be present but have 0 terminals."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=0,
            holes_top=0,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        layout = calculate_full_layout(config)
        assert len(layout.rails) > 0
        assert all(rail.terminal_count == 0 for rail in layout.rails)


# ================================================================
# Output tests with different material combinations
# ================================================================

class TestMaterialCombinationsValidation:
    """Validates various material combinations (terminals + holes)."""

    @pytest.mark.parametrize("terminals,holes_top,holes_bottom,holes_left,holes_right", [
        (0,  0,  0,  0,  0),
        (10, 0,  0,  0,  0),
        (0,  3,  3,  0,  0),
        (0,  0,  0,  2,  2),
        (16, 3,  3,  2,  2),
        (80, 0,  0,  0,  0),
        (40, 10, 10, 0,  0),
        (40, 0,  0,  5,  5),
        (40, 5,  5,  3,  3),
    ])
    def test_valid_combinations_for_ejb51(
        self, terminals, holes_top, holes_bottom, holes_left, holes_right
    ):
        """All listed material combinations must pass validation for EJB 51."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=terminals,
            holes_top=holes_top,
            holes_bottom=holes_bottom,
            holes_left=holes_left,
            holes_right=holes_right,
        )
        result = run_full_validation(config)
        assert result.is_valid, (
            f"Expected valid for terminals={terminals}, "
            f"top={holes_top}, bot={holes_bottom}, "
            f"left={holes_left}, right={holes_right}; "
            f"errors: {result.errors}"
        )

    def test_holes_only_no_terminals(self):
        """Configuration with holes but no terminals must be valid."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=0,
            holes_top=4,
            holes_bottom=4,
            holes_left=3,
            holes_right=3,
        )
        result = run_full_validation(config)
        assert result.is_valid

    def test_over_capacity_holes_top_fails(self):
        """Exceeding top hole capacity must fail validation."""
        config = ConfigurationInput(
            box_id="ejb21",
            terminals=0,
            holes_top=999,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        assert any(e.field == "holes_top" for e in result.errors)

    def test_over_capacity_holes_left_fails(self):
        """Exceeding left hole capacity must fail validation."""
        config = ConfigurationInput(
            box_id="ejb21",
            terminals=0,
            holes_top=0,
            holes_bottom=0,
            holes_left=999,
            holes_right=0,
        )
        result = run_full_validation(config)
        assert not result.is_valid
        assert any(e.field == "holes_left" for e in result.errors)

    def test_max_possible_reported_on_error(self):
        """Validation error for holes must include max_possible."""
        config = ConfigurationInput(
            box_id="ejb21",
            terminals=0,
            holes_top=999,
            holes_bottom=0,
            holes_left=0,
            holes_right=0,
        )
        result = run_full_validation(config)
        top_err = next(e for e in result.errors if e.field == "holes_top")
        assert top_err.max_possible is not None
        assert top_err.max_possible >= 0


class TestMaterialCombinationsLayout:
    """Verifies geometry for different material combinations."""

    def test_hole_positions_match_requested_counts(self):
        """Layout must return exactly as many hole positions as requested."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=16,
            holes_top=3,
            holes_bottom=4,
            holes_left=2,
            holes_right=1,
        )
        layout = calculate_full_layout(config)
        assert len(layout.holes_top) == 3
        assert len(layout.holes_bottom) == 4
        assert len(layout.holes_left) == 2
        assert len(layout.holes_right) == 1

    def test_hole_positions_have_coordinates(self):
        """Every hole position in the layout must carry x and y coordinates."""
        config = ConfigurationInput(
            box_id="ejb51",
            terminals=0,
            holes_top=2,
            holes_bottom=2,
            holes_left=2,
            holes_right=2,
        )
        layout = calculate_full_layout(config)
        for side in (layout.holes_top, layout.holes_bottom,
                     layout.holes_left, layout.holes_right):
            for hole in side:
                assert hole.x is not None
                assert hole.y is not None

    @pytest.mark.parametrize("box_id", [
        "ejb21", "ejb31", "ejb51", "ejb61", "ejb71", "ejb91"
    ])
    def test_all_box_models_layout_succeeds(self, box_id):
        """Layout calculation must succeed for every supported box model."""
        config = ConfigurationInput(
            box_id=box_id,
            terminals=10,
            holes_top=1,
            holes_bottom=1,
            holes_left=1,
            holes_right=1,
        )
        layout = calculate_full_layout(config)
        assert layout is not None
        assert len(layout.rails) > 0
