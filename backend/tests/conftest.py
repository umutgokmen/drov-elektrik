"""
Shared fixtures for all tests
"""
import sys
from pathlib import Path

import pytest

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models import get_all_box_models, get_box_model_by_id, HOLE_SIZES
from app.schemas import ConfigurationInput, HoleSideInput


@pytest.fixture
def all_boxes():
    return get_all_box_models()


@pytest.fixture(params=[b["id"] for b in __import__("app.models.box_models", fromlist=["BOX_MODELS_DATA"]).BOX_MODELS_DATA])
def box_id(request):
    return request.param


@pytest.fixture
def box(box_id):
    return get_box_model_by_id(box_id)


def make_config(box_id: str, **kwargs) -> ConfigurationInput:
    """Helper to build a ConfigurationInput with defaults"""
    defaults = {
        "box_id": box_id,
        "terminals": 0,
        "holes_top": 0,
        "holes_bottom": 0,
        "holes_left": 0,
        "holes_right": 0,
    }
    defaults.update(kwargs)
    return ConfigurationInput(**defaults)
