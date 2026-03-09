"""
Panel cover element data models.
Buttons, switches, indicator lamps, and other front panel mounted components.
All dimensions in mm.
"""
from typing import Dict, List, Optional
from enum import Enum


class CoverElementCategory(str, Enum):
    PUSHBUTTON = "pushbutton"
    SELECTOR_SWITCH = "selector_switch"
    INDICATOR_LAMP = "indicator_lamp"
    EMERGENCY_STOP = "emergency_stop"
    AMMETER = "ammeter"
    VOLTMETER = "voltmeter"


COVER_ELEMENTS_CATALOG: List[Dict] = [
    # ==================== PUSHBUTTONS ====================
    {
        "id": "btn-22-green",
        "name": "Yesil Buton 22mm",
        "category": "pushbutton",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 40,
        "color": "green",
        "function": "start",
    },
    {
        "id": "btn-22-red",
        "name": "Kirmizi Buton 22mm",
        "category": "pushbutton",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 40,
        "color": "red",
        "function": "stop",
    },
    {
        "id": "btn-22-yellow",
        "name": "Sari Buton 22mm",
        "category": "pushbutton",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 40,
        "color": "yellow",
        "function": "general",
    },
    {
        "id": "btn-22-blue",
        "name": "Mavi Buton 22mm",
        "category": "pushbutton",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 40,
        "color": "blue",
        "function": "reset",
    },
    {
        "id": "btn-22-white",
        "name": "Beyaz Buton 22mm",
        "category": "pushbutton",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 40,
        "color": "white",
        "function": "general",
    },
    # ==================== SELECTOR SWITCHES ====================
    {
        "id": "sel-22-2pos",
        "name": "2 Konumlu Anahtar 22mm",
        "category": "selector_switch",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 45,
        "positions": 2,
        "color": "black",
    },
    {
        "id": "sel-22-3pos",
        "name": "3 Konumlu Anahtar 22mm",
        "category": "selector_switch",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 45,
        "positions": 3,
        "color": "black",
    },
    # ==================== INDICATOR LAMPS ====================
    {
        "id": "lamp-22-green",
        "name": "Yesil Sinyal Lambasi 22mm",
        "category": "indicator_lamp",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 30,
        "color": "green",
        "voltage": [24, 230],
    },
    {
        "id": "lamp-22-red",
        "name": "Kirmizi Sinyal Lambasi 22mm",
        "category": "indicator_lamp",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 30,
        "color": "red",
        "voltage": [24, 230],
    },
    {
        "id": "lamp-22-yellow",
        "name": "Sari Sinyal Lambasi 22mm",
        "category": "indicator_lamp",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 30,
        "color": "yellow",
        "voltage": [24, 230],
    },
    {
        "id": "lamp-22-blue",
        "name": "Mavi Sinyal Lambasi 22mm",
        "category": "indicator_lamp",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 30,
        "color": "blue",
        "voltage": [24, 230],
    },
    {
        "id": "lamp-22-white",
        "name": "Beyaz Sinyal Lambasi 22mm",
        "category": "indicator_lamp",
        "cutout_diameter": 22,
        "bezel_diameter": 30,
        "depth_behind_panel": 30,
        "color": "white",
        "voltage": [24, 230],
    },
    # ==================== EMERGENCY STOP ====================
    {
        "id": "estop-40",
        "name": "Acil Stop Butonu 40mm",
        "category": "emergency_stop",
        "cutout_diameter": 22,
        "bezel_diameter": 40,
        "depth_behind_panel": 50,
        "color": "red",
        "function": "emergency_stop",
    },
    # ==================== METERS ====================
    {
        "id": "ammeter-72",
        "name": "Ampermetre 72x72mm",
        "category": "ammeter",
        "cutout_width": 68,
        "cutout_height": 68,
        "bezel_width": 72,
        "bezel_height": 72,
        "depth_behind_panel": 50,
        "color": "black",
    },
    {
        "id": "voltmeter-72",
        "name": "Voltmetre 72x72mm",
        "category": "voltmeter",
        "cutout_width": 68,
        "cutout_height": 68,
        "bezel_width": 72,
        "bezel_height": 72,
        "depth_behind_panel": 50,
        "color": "black",
    },
]


def get_all_cover_elements() -> List[Dict]:
    """Get all available cover elements"""
    return COVER_ELEMENTS_CATALOG


def get_cover_element_by_id(element_id: str) -> Optional[Dict]:
    """Get a specific cover element by ID"""
    for item in COVER_ELEMENTS_CATALOG:
        if item["id"] == element_id:
            return item
    return None


def get_cover_elements_by_category(category: str) -> List[Dict]:
    """Get all cover elements in a category"""
    return [item for item in COVER_ELEMENTS_CATALOG if item["category"] == category]
