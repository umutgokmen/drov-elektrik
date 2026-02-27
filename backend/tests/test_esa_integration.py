"""
Tests for ESA box type integration (issue #24):
- ESA data model entries
- STEP dimension extractor
- Validation service with ESA models
"""
import os
import textwrap
import pytest
from pathlib import Path

from app.models import get_all_box_models, get_box_model_by_id
from app.schemas import ConfigurationInput
from app.services.step_extractor import extract_dimensions_from_step
from app.services.validation.validation_service import run_full_validation

# Repository root is two levels above this file (backend/tests/...)
_REPO_ROOT = Path(__file__).resolve().parents[2]
STEP_EJB21 = str(
    _REPO_ROOT
    / "docs"
    / "15.Proje Çalışması - 4"
    / "Drov"
    / "02. Kutu Tipleri"
    / "01. EJB"
    / "01. Kutu 3D Step Dosyaları"
    / "EJB-21.stp"
)


# ── ESA Data Model ────────────────────────────────────────────────────────────

ESA_IDS = ["esa3", "esa4", "esa5", "esa6"]


@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_model_exists(box_id):
    """All ESA variants must be present in the model registry."""
    box = get_box_model_by_id(box_id)
    assert box is not None, f"Box model '{box_id}' not found"


@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_model_dimensions_positive(box_id):
    """ESA dimensions must all be strictly positive."""
    box = get_box_model_by_id(box_id)
    assert box.internal_length > 0
    assert box.internal_width > 0
    assert box.internal_depth > 0
    assert box.mounting_plate_x > 0
    assert box.mounting_plate_y > 0


@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_model_capacity_positive(box_id):
    """ESA capacity values must be non-negative and rail_count >= 1."""
    box = get_box_model_by_id(box_id)
    assert box.rail_count >= 1
    assert box.max_terminals >= 0
    assert box.max_holes_long >= 0
    assert box.max_holes_short >= 0


def test_esa_models_included_in_full_list():
    """get_all_box_models() must include every ESA entry."""
    all_ids = {b.id for b in get_all_box_models()}
    for box_id in ESA_IDS:
        assert box_id in all_ids


def test_esa_series_ascending_capacity():
    """Larger ESA models should have at least as many max_terminals as smaller ones."""
    models = [get_box_model_by_id(bid) for bid in ESA_IDS]
    for i in range(len(models) - 1):
        assert models[i].max_terminals <= models[i + 1].max_terminals, (
            f"{models[i].id} has more terminals than {models[i + 1].id}"
        )


# ── STEP Extractor ────────────────────────────────────────────────────────────


def test_step_extractor_file_not_found():
    """Should raise FileNotFoundError for a missing file."""
    with pytest.raises(FileNotFoundError):
        extract_dimensions_from_step("/nonexistent/path/model.stp")


def test_step_extractor_invalid_content(tmp_path):
    """Should raise ValueError when the file has no CARTESIAN_POINT data."""
    bad_file = tmp_path / "empty.stp"
    bad_file.write_text("ISO-10303-21;\nHEADER;\nENDSEC;\nDATA;\nENDSEC;\n")
    with pytest.raises(ValueError):
        extract_dimensions_from_step(str(bad_file))


def test_step_extractor_minimal_valid(tmp_path):
    """Should return dimensions from a minimal synthetic STEP snippet."""
    content = textwrap.dedent("""\
        ISO-10303-21;
        HEADER;
        ENDSEC;
        DATA;
        #1=CARTESIAN_POINT('',(0.0,0.0,0.0));
        #2=CARTESIAN_POINT('',(200.0,0.0,0.0));
        #3=CARTESIAN_POINT('',(200.0,150.0,0.0));
        #4=CARTESIAN_POINT('',(0.0,150.0,100.0));
        ENDSEC;
        END-ISO-10303-21;
    """)
    stp = tmp_path / "test.stp"
    stp.write_text(content)

    dims = extract_dimensions_from_step(str(stp))
    assert dims.length == 200.0
    assert dims.width == 150.0
    assert dims.depth == 100.0
    assert dims.source_file == "test.stp"


@pytest.mark.skipif(
    not os.path.exists(STEP_EJB21),
    reason="EJB-21 STEP file not available in this environment",
)
def test_step_extractor_ejb21_real_file():
    """Extractor must return positive non-zero spans from the EJB-21 STEP file."""
    dims = extract_dimensions_from_step(STEP_EJB21)
    assert dims.length > 0
    assert dims.width > 0
    assert dims.depth > 0


# ── Validation Service with ESA Models ───────────────────────────────────────

@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_zero_config_is_valid(box_id):
    """A zero-terminal, zero-hole configuration must pass validation for any ESA model."""
    config = ConfigurationInput(
        box_id=box_id,
        terminals=0,
        holes_top=0,
        holes_bottom=0,
        holes_left=0,
        holes_right=0,
    )
    result = run_full_validation(config)
    assert result.is_valid, f"Expected valid result for {box_id} but got: {result.errors}"


@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_max_terminals_is_valid(box_id):
    """Configuration at exactly max_terminals must pass validation."""
    box = get_box_model_by_id(box_id)
    config = ConfigurationInput(
        box_id=box_id,
        terminals=box.max_terminals,
        holes_top=0,
        holes_bottom=0,
        holes_left=0,
        holes_right=0,
    )
    result = run_full_validation(config)
    assert result.is_valid, f"Max terminal config invalid for {box_id}: {result.errors}"


@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_over_terminal_limit_is_invalid(box_id):
    """Exceeding max_terminals must produce a validation error."""
    box = get_box_model_by_id(box_id)
    config = ConfigurationInput(
        box_id=box_id,
        terminals=box.max_terminals + 50,
        holes_top=0,
        holes_bottom=0,
        holes_left=0,
        holes_right=0,
    )
    result = run_full_validation(config)
    assert not result.is_valid
    fields = [e.field for e in result.errors]
    assert "terminals" in fields


@pytest.mark.parametrize("box_id", ESA_IDS)
def test_esa_over_hole_limit_is_invalid(box_id):
    """Exceeding physical hole capacity on top must produce a validation error."""
    config = ConfigurationInput(
        box_id=box_id,
        terminals=0,
        holes_top=9999,
        holes_bottom=0,
        holes_left=0,
        holes_right=0,
    )
    result = run_full_validation(config)
    assert not result.is_valid
    fields = [e.field for e in result.errors]
    assert "holes_top" in fields


def test_esa_invalid_box_id_returns_error():
    """An unknown box_id must return a validation error."""
    config = ConfigurationInput(
        box_id="esa_nonexistent",
        terminals=0,
        holes_top=0,
        holes_bottom=0,
        holes_left=0,
        holes_right=0,
    )
    result = run_full_validation(config)
    assert not result.is_valid
    assert any(e.field == "box_id" for e in result.errors)
