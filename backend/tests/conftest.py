"""
Test configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def salt_malzeme_config():
    """Salt malzeme (terminals only, no holes) configuration for EJB 51"""
    return {
        "box_id": "ejb51",
        "terminals": 24,
        "holes_top": 0,
        "holes_bottom": 0,
        "holes_left": 0,
        "holes_right": 0,
    }


@pytest.fixture
def mixed_config():
    """Mixed configuration with terminals and cable entries for EJB 51"""
    return {
        "box_id": "ejb51",
        "terminals": 16,
        "holes_top": 3,
        "holes_bottom": 3,
        "holes_left": 2,
        "holes_right": 2,
    }
