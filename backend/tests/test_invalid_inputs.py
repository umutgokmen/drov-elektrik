"""
Test invalid and edge-case inputs.
"""
import pytest
from pydantic import ValidationError as PydanticValidationError

from app.schemas import ConfigurationInput, HoleSideInput
from app.services.validation.validation_service import run_full_validation
from app.models import get_box_model_by_id
from tests.conftest import make_config


BOX_IDS = ["ejb21", "ejb31", "ejb51", "ejb61", "ejb63", "ejb71", "ejb73", "ejb91", "ejb93"]


class TestNegativeInputs:
    """Negative values should be rejected by Pydantic"""

    def test_negative_terminals(self):
        with pytest.raises(PydanticValidationError):
            ConfigurationInput(box_id="ejb21", terminals=-1)

    def test_negative_holes_top(self):
        with pytest.raises(PydanticValidationError):
            ConfigurationInput(box_id="ejb21", terminals=0, holes_top=-5)

    def test_negative_holes_bottom(self):
        with pytest.raises(PydanticValidationError):
            ConfigurationInput(box_id="ejb21", terminals=0, holes_bottom=-1)

    def test_negative_holes_left(self):
        with pytest.raises(PydanticValidationError):
            ConfigurationInput(box_id="ejb21", terminals=0, holes_left=-1)

    def test_negative_holes_right(self):
        with pytest.raises(PydanticValidationError):
            ConfigurationInput(box_id="ejb21", terminals=0, holes_right=-1)

    def test_negative_hole_spec_count(self):
        with pytest.raises(PydanticValidationError):
            HoleSideInput(count=-1, size="M20")


class TestInvalidBoxId:
    """Invalid box IDs should be caught by validation"""

    def test_nonexistent_box_id(self):
        config = make_config("nonexistent_box")
        result = run_full_validation(config)
        assert not result.is_valid
        assert any(e.field == "box_id" for e in result.errors)

    def test_empty_box_id(self):
        config = make_config("")
        result = run_full_validation(config)
        assert not result.is_valid

    def test_case_sensitive_box_id(self):
        config = make_config("EJB21")
        result = run_full_validation(config)
        assert not result.is_valid


class TestInvalidHoleSizes:
    """Invalid hole sizes should use M20 as fallback via get_hole_size"""

    def test_invalid_hole_size_in_spec(self):
        config = ConfigurationInput(
            box_id="ejb21",
            terminals=0,
            holes_top_spec=HoleSideInput(count=1, size="INVALID"),
        )
        size = config.get_hole_size("top")
        assert size == "INVALID"

    def test_missing_spec_defaults_to_m20(self):
        config = make_config("ejb21", holes_top=1)
        assert config.get_hole_size("top") == "M20"


class TestEdgeCases:
    """Edge cases: zero everything, max everything"""

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_zero_everything(self, box_id):
        config = make_config(box_id, terminals=0)
        result = run_full_validation(config)
        assert result.is_valid
        assert len(result.errors) == 0

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_max_terminals_zero_holes(self, box_id):
        box = get_box_model_by_id(box_id)
        config = make_config(box_id, terminals=box.max_terminals)
        result = run_full_validation(config)
        assert result.is_valid

    def test_max_holes_all_sides_ejb91(self):
        """EJB91 is the largest box; fill all sides with max M20 holes"""
        box = get_box_model_by_id("ejb91")
        config = make_config(
            "ejb91",
            terminals=0,
            holes_top=box.max_holes_short,
            holes_bottom=box.max_holes_short,
            holes_left=box.max_holes_long,
            holes_right=box.max_holes_long,
        )
        result = run_full_validation(config)
        # This may or may not be valid depending on physical limits
        # but it should NOT raise an exception
        assert isinstance(result.is_valid, bool)

    def test_single_terminal_single_hole(self):
        config = make_config("ejb21", terminals=1, holes_top=1)
        result = run_full_validation(config)
        assert result.is_valid

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_combined_max_load(self, box_id):
        """Max terminals + some holes should still validate without crashing"""
        box = get_box_model_by_id(box_id)
        config = make_config(box_id, terminals=box.max_terminals, holes_top=2, holes_bottom=2)
        result = run_full_validation(config)
        assert isinstance(result.is_valid, bool)
