"""
Box model data - Engineering constants for EJB, EJBX, and EJC Series
All units are in millimeters (mm)
"""
from typing import Dict, List, Optional
from app.schemas import BoxModel, EJCBoxModel


# Static box model data (will be moved to database later)
_EJB_MODELS_DATA: List[Dict] = [
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
        "max_terminals": 30
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

# EJBX series model data (dimensions are placeholders pending customer STEP files)
EJBX_MODELS_DATA: List[Dict] = [
    {
        "id": "ejbx1",
        "name": "EJBX 1",
        "internal_length": 200,
        "internal_width": 160,
        "internal_depth": 120,
        "mounting_plate_x": 240,
        "mounting_plate_y": 180,
        "max_holes_long": 8,
        "max_holes_short": 6,
        "rail_count": 1,
        "max_terminals": 20
    },
    {
        "id": "ejbx2",
        "name": "EJBX 2",
        "internal_length": 300,
        "internal_width": 230,
        "internal_depth": 150,
        "mounting_plate_x": 340,
        "mounting_plate_y": 260,
        "max_holes_long": 16,
        "max_holes_short": 10,
        "rail_count": 2,
        "max_terminals": 40
    },
    {
        "id": "ejbx3",
        "name": "EJBX 3",
        "internal_length": 400,
        "internal_width": 310,
        "internal_depth": 200,
        "mounting_plate_x": 450,
        "mounting_plate_y": 340,
        "max_holes_long": 24,
        "max_holes_short": 14,
        "rail_count": 2,
        "max_terminals": 60
    },
    {
        "id": "ejbx4",
        "name": "EJBX 4",
        "internal_length": 500,
        "internal_width": 400,
        "internal_depth": 250,
        "mounting_plate_x": 560,
        "mounting_plate_y": 440,
        "max_holes_long": 32,
        "max_holes_short": 18,
        "rail_count": 3,
        "max_terminals": 80
    },
]

BOX_MODELS_DATA = _EJB_MODELS_DATA + EJBX_MODELS_DATA

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
        "clearance": 5  # Minimum gap between holes
    },
    "RAIL_DIN": {
        "name": "DIN Rail NS 35",
        "height": 35,
        "depth": 7.5
    }
}

# Salt malzeme (standard/fixed) components included with every EJB enclosure
SALT_MALZEME_COMPONENTS = [
    {
        "part_name": "EJB Cover",
        "part_code": "EJB-COVER",
        "quantity": 1,
        "description": "Enclosure cover/lid"
    },
    {
        "part_name": "CLIPFIX 35/5 End Clamp",
        "part_code": "pnl_302203_CLIPFIX-35-5",
        "quantity": 2,
        "description": "DIN rail end clamp (2 per rail end)"
    },
    {
        "part_name": "Drain Valve M20x1.5",
        "part_code": "Drain_Valve_M20x1.5mm",
        "quantity": 1,
        "description": "Condensate drain valve M20x1.5mm"
    },
]


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


# EJC-specific hole drilling constants (tighter tolerances than EJB)
EJC_MIN_EDGE_MARGIN = 20       # 20mm from box edge (EJC has thicker walls)
EJC_MIN_HOLE_CLEARANCE = 8     # 8mm minimum gap between holes on EJC
EJC_MAX_HOLE_DIAMETER = 25     # M25 max for EJC series

# EJC box model data
# Dimensions are placeholders pending customer-supplied STEP files (see issue #27 blocker)
EJC_BOX_MODELS_DATA: List[Dict] = [
    {
        "id": "ejc01",
        "name": "EJC 01",
        "internal_length": 150,
        "internal_width": 150,
        "internal_depth": 80,
        "mounting_plate_x": 160,
        "mounting_plate_y": 160,
        "max_holes_long": 4,
        "max_holes_short": 4,
        "rail_count": 1,
        "max_terminals": 16,
        "ip_rating": "IP66",
        "has_earth_plate": True,
    },
    {
        "id": "ejc02",
        "name": "EJC 02",
        "internal_length": 200,
        "internal_width": 150,
        "internal_depth": 80,
        "mounting_plate_x": 210,
        "mounting_plate_y": 160,
        "max_holes_long": 6,
        "max_holes_short": 4,
        "rail_count": 1,
        "max_terminals": 24,
        "ip_rating": "IP66",
        "has_earth_plate": True,
    },
    {
        "id": "ejc03",
        "name": "EJC 03",
        "internal_length": 200,
        "internal_width": 200,
        "internal_depth": 100,
        "mounting_plate_x": 210,
        "mounting_plate_y": 210,
        "max_holes_long": 6,
        "max_holes_short": 6,
        "rail_count": 1,
        "max_terminals": 30,
        "ip_rating": "IP66",
        "has_earth_plate": True,
    },
    {
        "id": "ejc04",
        "name": "EJC 04",
        "internal_length": 300,
        "internal_width": 200,
        "internal_depth": 120,
        "mounting_plate_x": 310,
        "mounting_plate_y": 210,
        "max_holes_long": 10,
        "max_holes_short": 6,
        "rail_count": 2,
        "max_terminals": 50,
        "ip_rating": "IP66",
        "has_earth_plate": True,
    },
]


def get_all_ejc_box_models() -> List[EJCBoxModel]:
    """Get all available EJC box models"""
    return [EJCBoxModel(**data) for data in EJC_BOX_MODELS_DATA]


def get_ejc_box_model_by_id(box_id: str) -> Optional[EJCBoxModel]:
    """Get a specific EJC box model by ID"""
    for data in EJC_BOX_MODELS_DATA:
        if data["id"] == box_id:
            return EJCBoxModel(**data)
    return None
