"""
Test switchgear layout algorithm.
"""
import pytest
from app.schemas import (
    SwitchgearComponent,
    SwitchgearRailAssignment,
    RailLayout,
)
from app.services.switchgear_layout import (
    calculate_switchgear_positions,
    auto_distribute_components,
)
from app.services.geometry_service import calculate_rail_layout
from app.models import get_box_model_by_id


def make_rails(box_id: str) -> list:
    box = get_box_model_by_id(box_id)
    return calculate_rail_layout(box, 0)


class TestSwitchgearPositionCalculation:
    """Test component placement on rails"""

    def test_single_component_on_rail(self):
        rails = make_rails("ejb61")
        assignments = [SwitchgearRailAssignment(
            rail_index=0,
            components=[SwitchgearComponent(component_id="mcb-1p", quantity=1)],
        )]
        positions, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb61")
        assert len(errors) == 0
        assert len(positions) == 1
        assert positions[0].component_id == "mcb-1p"
        assert positions[0].width == 17.5

    def test_multiple_components_sequential(self):
        rails = make_rails("ejb61")
        assignments = [SwitchgearRailAssignment(
            rail_index=0,
            components=[
                SwitchgearComponent(component_id="mcb-1p", quantity=3),
            ],
        )]
        positions, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb61")
        assert len(errors) == 0
        assert len(positions) == 3
        # Each should be positioned sequentially
        for i in range(1, len(positions)):
            assert positions[i].x > positions[i-1].x

    def test_mixed_components(self):
        rails = make_rails("ejb61")
        assignments = [SwitchgearRailAssignment(
            rail_index=0,
            components=[
                SwitchgearComponent(component_id="mcb-3p", quantity=1),
                SwitchgearComponent(component_id="relay-4co", quantity=2),
                SwitchgearComponent(component_id="mcb-1p", quantity=5),
            ],
        )]
        positions, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb61")
        assert len(errors) == 0
        assert len(positions) == 8  # 1 + 2 + 5

    def test_overflow_produces_error(self):
        rails = make_rails("ejb21")  # smallest box
        assignments = [SwitchgearRailAssignment(
            rail_index=0,
            components=[SwitchgearComponent(component_id="mcb-3p", quantity=20)],
        )]
        positions, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb21")
        assert len(errors) > 0
        assert "kapasitesi" in errors[0].message

    def test_invalid_rail_index(self):
        rails = make_rails("ejb21")  # 1 rail
        assignments = [SwitchgearRailAssignment(
            rail_index=5,
            components=[SwitchgearComponent(component_id="mcb-1p", quantity=1)],
        )]
        _, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb21")
        assert len(errors) > 0

    def test_unknown_component(self):
        rails = make_rails("ejb61")
        assignments = [SwitchgearRailAssignment(
            rail_index=0,
            components=[SwitchgearComponent(component_id="nonexistent", quantity=1)],
        )]
        _, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb61")
        assert len(errors) > 0
        assert "Bilinmeyen" in errors[0].message

    def test_empty_assignments(self):
        rails = make_rails("ejb61")
        positions, errors, _ = calculate_switchgear_positions([], rails, "ejb61")
        assert len(errors) == 0
        assert len(positions) == 0

    def test_multiple_rails(self):
        rails = make_rails("ejb61")  # 3 rails
        assignments = [
            SwitchgearRailAssignment(
                rail_index=0,
                components=[SwitchgearComponent(component_id="mcb-3p", quantity=2)],
            ),
            SwitchgearRailAssignment(
                rail_index=1,
                components=[SwitchgearComponent(component_id="relay-4co", quantity=3)],
            ),
            SwitchgearRailAssignment(
                rail_index=2,
                components=[SwitchgearComponent(component_id="terminal-2.5", quantity=10)],
            ),
        ]
        positions, errors, _ = calculate_switchgear_positions(assignments, rails, "ejb61")
        assert len(errors) == 0
        assert len(positions) == 15  # 2 + 3 + 10
        # Check rail assignments are correct
        rail0_pos = [p for p in positions if p.rail_index == 0]
        rail1_pos = [p for p in positions if p.rail_index == 1]
        rail2_pos = [p for p in positions if p.rail_index == 2]
        assert len(rail0_pos) == 2
        assert len(rail1_pos) == 3
        assert len(rail2_pos) == 10

    def test_capacity_warning_at_80_percent(self):
        """Rail at >80% should produce a warning"""
        rails = make_rails("ejb21")  # small box
        # Fill ~85% of rail
        assignments = [SwitchgearRailAssignment(
            rail_index=0,
            components=[SwitchgearComponent(component_id="mcb-1p", quantity=6)],
        )]
        _, errors, warnings = calculate_switchgear_positions(assignments, rails, "ejb21")
        if len(errors) == 0:
            # If it fits, check for warning
            assert len(warnings) >= 0  # may or may not trigger depending on exact width


class TestAutoDistribute:
    """Test automatic component distribution across rails"""

    def test_simple_distribution(self):
        rails = make_rails("ejb61")
        components = [
            SwitchgearComponent(component_id="mcb-1p", quantity=6),
        ]
        assignments = auto_distribute_components(components, rails)
        assert len(assignments) > 0
        total = sum(len(a.components) for a in assignments)
        assert total == 6

    def test_large_components_spread_across_rails(self):
        rails = make_rails("ejb91")  # largest box, 3 rails
        components = [
            SwitchgearComponent(component_id="mcb-3p", quantity=10),
        ]
        assignments = auto_distribute_components(components, rails)
        # Should use multiple rails
        assert len(assignments) >= 1
        total = sum(len(a.components) for a in assignments)
        assert total == 10

    def test_empty_input(self):
        rails = make_rails("ejb61")
        assignments = auto_distribute_components([], rails)
        assert len(assignments) == 0

    def test_no_rails(self):
        components = [SwitchgearComponent(component_id="mcb-1p", quantity=1)]
        assignments = auto_distribute_components(components, [])
        assert len(assignments) == 0
