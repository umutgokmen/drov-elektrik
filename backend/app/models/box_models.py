"""
Box model data - Engineering constants for EJB, EJBX, ESP, ESA, ESX, and EJC Series
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
    },
]

# ESP series - dimensions are estimated pending customer STEP file delivery (issue #23)
ESP_MODELS_DATA: List[Dict] = [
    {
        "id": "esp1",
        "name": "ESP 1",
        "internal_length": 120,
        "internal_width": 80,
        "internal_depth": 60,
        "mounting_plate_x": 100,
        "mounting_plate_y": 60,
        "max_holes_long": 3,
        "max_holes_short": 2,
        "rail_count": 1,
        "max_terminals": 7
    },
    {
        "id": "esp2",
        "name": "ESP 2",
        "internal_length": 150,
        "internal_width": 100,
        "internal_depth": 80,
        "mounting_plate_x": 130,
        "mounting_plate_y": 80,
        "max_holes_long": 4,
        "max_holes_short": 3,
        "rail_count": 1,
        "max_terminals": 11
    },
    {
        "id": "esp3",
        "name": "ESP 3",
        "internal_length": 200,
        "internal_width": 150,
        "internal_depth": 100,
        "mounting_plate_x": 180,
        "mounting_plate_y": 110,
        "max_holes_long": 7,
        "max_holes_short": 5,
        "rail_count": 1,
        "max_terminals": 21
    },
    {
        "id": "esp4",
        "name": "ESP 4",
        "internal_length": 300,
        "internal_width": 200,
        "internal_depth": 120,
        "mounting_plate_x": 280,
        "mounting_plate_y": 160,
        "max_holes_long": 11,
        "max_holes_short": 7,
        "rail_count": 2,
        "max_terminals": 40
    },
    {
        "id": "esp5",
        "name": "ESP 5",
        "internal_length": 400,
        "internal_width": 300,
        "internal_depth": 150,
        "mounting_plate_x": 380,
        "mounting_plate_y": 240,
        "max_holes_long": 15,
        "max_holes_short": 11,
        "rail_count": 2,
        "max_terminals": 60
    },
]

# ESA series - dimensions are engineering estimates pending customer STEP files (issue #24)
ESA_MODELS_DATA: List[Dict] = [
    {
        "id": "esa1",
        "name": "ESA 1",
        "internal_length": 300,
        "internal_width": 300,
        "internal_depth": 180,
        "mounting_plate_x": 340,
        "mounting_plate_y": 220,
        "max_holes_long": 14,
        "max_holes_short": 14,
        "rail_count": 2,
        "max_terminals": 50
    },
    {
        "id": "esa2",
        "name": "ESA 2",
        "internal_length": 400,
        "internal_width": 350,
        "internal_depth": 200,
        "mounting_plate_x": 440,
        "mounting_plate_y": 260,
        "max_holes_long": 22,
        "max_holes_short": 18,
        "rail_count": 2,
        "max_terminals": 70
    },
    {
        "id": "esa3",
        "name": "ESA 3",
        "internal_length": 250,
        "internal_width": 200,
        "internal_depth": 150,
        "mounting_plate_x": 270,
        "mounting_plate_y": 220,
        "max_holes_long": 18,
        "max_holes_short": 12,
        "rail_count": 1,
        "max_terminals": 28
    },
    {
        "id": "esa4",
        "name": "ESA 4",
        "internal_length": 350,
        "internal_width": 300,
        "internal_depth": 200,
        "mounting_plate_x": 370,
        "mounting_plate_y": 320,
        "max_holes_long": 24,
        "max_holes_short": 20,
        "rail_count": 2,
        "max_terminals": 52
    },
    {
        "id": "esa5",
        "name": "ESA 5",
        "internal_length": 450,
        "internal_width": 400,
        "internal_depth": 250,
        "mounting_plate_x": 470,
        "mounting_plate_y": 420,
        "max_holes_long": 32,
        "max_holes_short": 28,
        "rail_count": 2,
        "max_terminals": 76
    },
    {
        "id": "esa6",
        "name": "ESA 6",
        "internal_length": 550,
        "internal_width": 450,
        "internal_depth": 300,
        "mounting_plate_x": 570,
        "mounting_plate_y": 470,
        "max_holes_long": 42,
        "max_holes_short": 32,
        "rail_count": 3,
        "max_terminals": 96
    },
]

# ESX series stainless steel - dimensions are placeholder pending customer STEP files (issue #25)
ESX_MODELS_DATA: List[Dict] = [
    {
        "id": "esx1",
        "name": "ESX 1",
        "internal_length": 400,
        "internal_width": 400,
        "internal_depth": 220,
        "mounting_plate_x": 440,
        "mounting_plate_y": 280,
        "max_holes_long": 22,
        "max_holes_short": 22,
        "rail_count": 2,
        "max_terminals": 60
    },
    {
        "id": "esx2",
        "name": "ESX 2",
        "internal_length": 500,
        "internal_width": 450,
        "internal_depth": 250,
        "mounting_plate_x": 550,
        "mounting_plate_y": 320,
        "max_holes_long": 30,
        "max_holes_short": 26,
        "rail_count": 3,
        "max_terminals": 90
    },
    {
        "id": "esx15",
        "name": "ESX 15",
        "internal_length": 150,
        "internal_width": 150,
        "internal_depth": 80,
        "mounting_plate_x": 130,
        "mounting_plate_y": 130,
        "max_holes_long": 4,
        "max_holes_short": 4,
        "rail_count": 1,
        "max_terminals": 16
    },
    {
        "id": "esx20",
        "name": "ESX 20",
        "internal_length": 200,
        "internal_width": 200,
        "internal_depth": 100,
        "mounting_plate_x": 180,
        "mounting_plate_y": 180,
        "max_holes_long": 6,
        "max_holes_short": 6,
        "rail_count": 1,
        "max_terminals": 24
    },
    {
        "id": "esx30",
        "name": "ESX 30",
        "internal_length": 300,
        "internal_width": 250,
        "internal_depth": 150,
        "mounting_plate_x": 280,
        "mounting_plate_y": 230,
        "max_holes_long": 8,
        "max_holes_short": 6,
        "rail_count": 2,
        "max_terminals": 40
    },
    {
        "id": "esx40",
        "name": "ESX 40",
        "internal_length": 400,
        "internal_width": 300,
        "internal_depth": 200,
        "mounting_plate_x": 380,
        "mounting_plate_y": 280,
        "max_holes_long": 10,
        "max_holes_short": 8,
        "rail_count": 2,
        "max_terminals": 56
    },
]

# EJBX series model data (dimensions are placeholders pending customer STEP files, issue #26)
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

BOX_MODELS_DATA = _EJB_MODELS_DATA + ESP_MODELS_DATA + ESA_MODELS_DATA + ESX_MODELS_DATA + EJBX_MODELS_DATA

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

# Series-specific engineering limits for ESP (tighter than EJB due to smaller body)
ESP_HOLE_RULES = {
    "min_edge_margin": 12,    # mm from box edge
    "min_hole_clearance": 4,  # mm between holes
    "hole_diameter": 20,      # M20 standard
}

EJB_HOLE_RULES = {
    "min_edge_margin": 15,
    "min_hole_clearance": 5,
    "hole_diameter": 20,
}


def get_hole_rules(box_id: str) -> dict:
    """Return series-specific hole rules for a given box ID."""
    if box_id.startswith("esp"):
        return ESP_HOLE_RULES
    return EJB_HOLE_RULES

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
