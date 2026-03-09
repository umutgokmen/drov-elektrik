"""
Switchgear component data models.
Fuse, relay, switch, contactor, and other DIN-rail mounted components.
All dimensions in mm.
"""
from typing import Dict, List, Optional
from enum import Enum


class SwitchgearCategory(str, Enum):
    FUSE = "fuse"
    MCB = "mcb"  # miniature circuit breaker
    RELAY = "relay"
    CONTACTOR = "contactor"
    SWITCH = "switch"
    TERMINAL = "terminal"
    SURGE_PROTECTOR = "surge_protector"
    TIMER = "timer"
    POWER_SUPPLY = "power_supply"


# DIN rail module width: 17.5mm (standard DIN module)
DIN_MODULE_WIDTH = 17.5


SWITCHGEAR_CATALOG: List[Dict] = [
    # ==================== FUSES ====================
    {
        "id": "fuse-nh00",
        "name": "NH00 Sigorta Yuvas",
        "category": "fuse",
        "brand": "Generic",
        "din_modules": 3,
        "width": 52.5,
        "height": 70,
        "depth": 62,
        "current_rating": [16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    {
        "id": "fuse-nh1",
        "name": "NH1 Sigorta Yuvas",
        "category": "fuse",
        "brand": "Generic",
        "din_modules": 3,
        "width": 52.5,
        "height": 70,
        "depth": 70,
        "current_rating": [63, 80, 100, 125, 160, 200, 250],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    # ==================== MCBs ====================
    {
        "id": "mcb-1p",
        "name": "Otomatik Sigorta 1P",
        "category": "mcb",
        "brand": "Generic",
        "din_modules": 1,
        "width": 17.5,
        "height": 80,
        "depth": 68,
        "current_rating": [6, 10, 16, 20, 25, 32, 40, 50, 63],
        "pole_count": 1,
        "mounting": "din_rail",
    },
    {
        "id": "mcb-2p",
        "name": "Otomatik Sigorta 2P",
        "category": "mcb",
        "brand": "Generic",
        "din_modules": 2,
        "width": 35.0,
        "height": 80,
        "depth": 68,
        "current_rating": [6, 10, 16, 20, 25, 32, 40, 50, 63],
        "pole_count": 2,
        "mounting": "din_rail",
    },
    {
        "id": "mcb-3p",
        "name": "Otomatik Sigorta 3P",
        "category": "mcb",
        "brand": "Generic",
        "din_modules": 3,
        "width": 52.5,
        "height": 80,
        "depth": 68,
        "current_rating": [6, 10, 16, 20, 25, 32, 40, 50, 63],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    {
        "id": "mcb-4p",
        "name": "Otomatik Sigorta 4P",
        "category": "mcb",
        "brand": "Generic",
        "din_modules": 4,
        "width": 70.0,
        "height": 80,
        "depth": 68,
        "current_rating": [6, 10, 16, 20, 25, 32, 40, 50, 63],
        "pole_count": 4,
        "mounting": "din_rail",
    },
    # ==================== RELAYS ====================
    {
        "id": "relay-4co",
        "name": "Ara Role 4CO",
        "category": "relay",
        "brand": "Generic",
        "din_modules": 1,
        "width": 17.5,
        "height": 80,
        "depth": 62,
        "coil_voltage": [24, 48, 110, 230],
        "contact_count": 4,
        "pole_count": 1,
        "mounting": "din_rail",
    },
    {
        "id": "relay-2co",
        "name": "Ara Role 2CO",
        "category": "relay",
        "brand": "Generic",
        "din_modules": 1,
        "width": 15.5,
        "height": 80,
        "depth": 62,
        "coil_voltage": [24, 48, 110, 230],
        "contact_count": 2,
        "pole_count": 1,
        "mounting": "din_rail",
    },
    # ==================== CONTACTORS ====================
    {
        "id": "contactor-9a",
        "name": "Kontaktor 9A",
        "category": "contactor",
        "brand": "Generic",
        "din_modules": 3,
        "width": 45,
        "height": 82,
        "depth": 77,
        "current_rating": [9],
        "coil_voltage": [24, 48, 110, 230],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    {
        "id": "contactor-18a",
        "name": "Kontaktor 18A",
        "category": "contactor",
        "brand": "Generic",
        "din_modules": 3,
        "width": 45,
        "height": 82,
        "depth": 77,
        "current_rating": [18],
        "coil_voltage": [24, 48, 110, 230],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    {
        "id": "contactor-32a",
        "name": "Kontaktor 32A",
        "category": "contactor",
        "brand": "Generic",
        "din_modules": 3,
        "width": 55,
        "height": 95,
        "depth": 85,
        "current_rating": [32],
        "coil_voltage": [24, 48, 110, 230],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    # ==================== SWITCHES ====================
    {
        "id": "switch-isolator-3p",
        "name": "Yuk Ayirici 3P",
        "category": "switch",
        "brand": "Generic",
        "din_modules": 3,
        "width": 52.5,
        "height": 80,
        "depth": 68,
        "current_rating": [25, 32, 40, 63, 80, 100],
        "pole_count": 3,
        "mounting": "din_rail",
    },
    # ==================== TERMINALS ====================
    {
        "id": "terminal-2.5",
        "name": "UT 2,5 Klemens",
        "category": "terminal",
        "brand": "Phoenix Contact",
        "din_modules": 0,
        "width": 5.2,
        "height": 47.7,
        "depth": 47.5,
        "cross_section": 2.5,
        "pole_count": 1,
        "mounting": "din_rail",
    },
    {
        "id": "terminal-4",
        "name": "UT 4 Klemens",
        "category": "terminal",
        "brand": "Phoenix Contact",
        "din_modules": 0,
        "width": 6.2,
        "height": 47.7,
        "depth": 47.5,
        "cross_section": 4,
        "pole_count": 1,
        "mounting": "din_rail",
    },
    {
        "id": "terminal-6",
        "name": "UT 6 Klemens",
        "category": "terminal",
        "brand": "Phoenix Contact",
        "din_modules": 0,
        "width": 8.2,
        "height": 52.3,
        "depth": 51.9,
        "cross_section": 6,
        "pole_count": 1,
        "mounting": "din_rail",
    },
    # ==================== SURGE PROTECTORS ====================
    {
        "id": "surge-type2",
        "name": "Tip 2 Parafudr",
        "category": "surge_protector",
        "brand": "Generic",
        "din_modules": 4,
        "width": 70,
        "height": 90,
        "depth": 65,
        "pole_count": 3,
        "mounting": "din_rail",
    },
    # ==================== TIMERS ====================
    {
        "id": "timer-digital",
        "name": "Dijital Zaman Rolesi",
        "category": "timer",
        "brand": "Generic",
        "din_modules": 1,
        "width": 17.5,
        "height": 90,
        "depth": 62,
        "coil_voltage": [24, 230],
        "pole_count": 1,
        "mounting": "din_rail",
    },
    # ==================== POWER SUPPLY ====================
    {
        "id": "psu-24v-2.5a",
        "name": "24V 2.5A Guc Kaynagi",
        "category": "power_supply",
        "brand": "Generic",
        "din_modules": 2,
        "width": 35,
        "height": 90,
        "depth": 55,
        "output_voltage": 24,
        "output_current": 2.5,
        "pole_count": 1,
        "mounting": "din_rail",
    },
]


def get_all_switchgear() -> List[Dict]:
    """Get all available switchgear components"""
    return SWITCHGEAR_CATALOG


def get_switchgear_by_id(component_id: str) -> Optional[Dict]:
    """Get a specific switchgear component by ID"""
    for item in SWITCHGEAR_CATALOG:
        if item["id"] == component_id:
            return item
    return None


def get_switchgear_by_category(category: str) -> List[Dict]:
    """Get all switchgear components in a category"""
    return [item for item in SWITCHGEAR_CATALOG if item["category"] == category]
