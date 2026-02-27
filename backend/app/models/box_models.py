"""
Box model data - Engineering constants for EJB Series
All units are in millimeters (mm)
"""
from typing import Dict, List, Optional
from app.schemas import BoxModel


# Static box model data (will be moved to database later)
BOX_MODELS_DATA: List[Dict] = [
    {
        "id": "ejb21",
        "name": "EJB 21",
        "internal_length": 169,
        "internal_width": 179,
        "internal_depth": 160,
        "mounting_plate_x": 180,
        "mounting_plate_y": 140,
        "max_holes_long": 10,
        "max_holes_short": 8,
        "rail_count": 1,
        "max_terminals": 26
    },
    {
        "id": "ejb31",
        "name": "EJB 31",
        "internal_length": 249,
        "internal_width": 258,
        "internal_depth": 294,
        "mounting_plate_x": 325,
        "mounting_plate_y": 225,
        "max_holes_long": 28,
        "max_holes_short": 20,
        "rail_count": 2,
        "max_terminals": 52
    },
    {
        "id": "ejb51",
        "name": "EJB 51",
        "internal_length": 390,
        "internal_width": 388,
        "internal_depth": 370,
        "mounting_plate_x": 460,
        "mounting_plate_y": 260,
        "max_holes_long": 44,
        "max_holes_short": 24,
        "rail_count": 2,
        "max_terminals": 80
    },
    {
        "id": "ejb61",
        "name": "EJB 61",
        "internal_length": 500,
        "internal_width": 470,
        "internal_depth": 360,
        "mounting_plate_x": 560,
        "mounting_plate_y": 360,
        "max_holes_long": 72,
        "max_holes_short": 48,
        "rail_count": 3,
        "max_terminals": 92
    },
    {
        "id": "ejb63",
        "name": "EJB 63",
        "internal_length": 500,
        "internal_width": 470,
        "internal_depth": 360,
        "mounting_plate_x": 560,
        "mounting_plate_y": 360,
        "max_holes_long": 36,
        "max_holes_short": 24,
        "rail_count": 3,
        "max_terminals": 92
    },
    {
        "id": "ejb71",
        "name": "EJB 71",
        "internal_length": 600,
        "internal_width": 530,
        "internal_depth": 410,
        "mounting_plate_x": 650,
        "mounting_plate_y": 410,
        "max_holes_long": 90,
        "max_holes_short": 59,
        "rail_count": 3,
        "max_terminals": 110
    },
    {
        "id": "ejb73",
        "name": "EJB 73",
        "internal_length": 600,
        "internal_width": 530,
        "internal_depth": 410,
        "mounting_plate_x": 650,
        "mounting_plate_y": 410,
        "max_holes_long": 40,
        "max_holes_short": 16,
        "rail_count": 3,
        "max_terminals": 110
    },
    {
        "id": "ejb91",
        "name": "EJB 91",
        "internal_length": 700,
        "internal_width": 650,
        "internal_depth": 510,
        "mounting_plate_x": 750,
        "mounting_plate_y": 440,
        "max_holes_long": 112,
        "max_holes_short": 70,
        "rail_count": 3,
        "max_terminals": 140
    },
    {
        "id": "ejb93",
        "name": "EJB 93",
        "internal_length": 700,
        "internal_width": 650,
        "internal_depth": 510,
        "mounting_plate_x": 750,
        "mounting_plate_y": 440,
        "max_holes_long": 48,
        "max_holes_short": 30,
        "rail_count": 3,
        "max_terminals": 140
    }
]

# Component specifications
COMPONENTS = {
    "TERMINAL_2_5": {
        "name": "UT 2,5 Terminal",
        "width": 5.2,
        "height": 47.7,
        "depth": 47.5
    },
    "HOLE_M20": {
        "name": "M20 Hole",
        "diameter": 20,
        "clearance": 5
    },
    "RAIL_DIN": {
        "name": "DIN Rail NS 35",
        "height": 35,
        "depth": 7.5
    }
}

# Supported hole sizes (metric cable gland sizes)
HOLE_SIZES = {
    "M20": {"diameter": 20, "clearance": 5, "name": "M20 Cable Gland", "code": "M20-GL"},
    "M25": {"diameter": 25, "clearance": 6, "name": "M25 Cable Gland", "code": "M25-GL"},
    "M32": {"diameter": 32, "clearance": 8, "name": "M32 Cable Gland", "code": "M32-GL"},
    "M40": {"diameter": 40, "clearance": 10, "name": "M40 Cable Gland", "code": "M40-GL"},
    "M50": {"diameter": 50, "clearance": 12, "name": "M50 Cable Gland", "code": "M50-GL"},
}


def get_all_box_models() -> List[BoxModel]:
    """Get all available box models"""
    return [BoxModel(**data) for data in BOX_MODELS_DATA]


def get_box_model_by_id(box_id: str) -> Optional[BoxModel]:
    """Get a specific box model by ID"""
    for data in BOX_MODELS_DATA:
        if data["id"] == box_id:
            return BoxModel(**data)
    return None


def get_component(component_name: str) -> Optional[Dict]:
    """Get component specifications"""
    return COMPONENTS.get(component_name)
