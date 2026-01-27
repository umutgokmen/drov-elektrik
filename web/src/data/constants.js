/**
 * Engineering constants for Drov Pilot Project (EJB Series)
 * All units are in millimeters (mm)
 */

export const BOX_MODELS = [
    {
        id: "ejb21",
        name: "EJB 21",
        internalLength: 169, // Long side
        internalWidth: 179,  // Short side
        internalDepth: 160,
        mountingPlate: { x: 180, y: 140 }, // Note: Plate might be larger than cavity in some series, using cavity for drawing
        maxHolesLong: 10,
        maxHolesShort: 8,
        railCount: 1,
        maxTerminals: 30
    },
    {
        id: "ejb31",
        name: "EJB 31",
        internalLength: 249,
        internalWidth: 258,
        internalDepth: 294,
        mountingPlate: { x: 325, y: 225 },
        maxHolesLong: 28,
        maxHolesShort: 20,
        railCount: 2,
        maxTerminals: 52
    },
    {
        id: "ejb51",
        name: "EJB 51",
        internalLength: 390,
        internalWidth: 388,
        internalDepth: 370,
        mountingPlate: { x: 460, y: 260 },
        maxHolesLong: 44,
        maxHolesShort: 24,
        railCount: 2,
        maxTerminals: 80
    },
    {
        id: "ejb61",
        name: "EJB 61",
        internalLength: 500,
        internalWidth: 470,
        internalDepth: 360,
        mountingPlate: { x: 560, y: 360 },
        maxHolesLong: 72,
        maxHolesShort: 48,
        railCount: 3,
        maxTerminals: 92
    },
    {
        id: "ejb63",
        name: "EJB 63",
        internalLength: 500,
        internalWidth: 470,
        internalDepth: 360,
        mountingPlate: { x: 560, y: 360 },
        maxHolesLong: 36,
        maxHolesShort: 24,
        railCount: 3,
        maxTerminals: 92
    },
    {
        id: "ejb71",
        name: "EJB 71",
        internalLength: 600,
        internalWidth: 530,
        internalDepth: 410,
        mountingPlate: { x: 650, y: 410 },
        maxHolesLong: 90,
        maxHolesShort: 59,
        railCount: 3,
        maxTerminals: 110
    },
    {
        id: "ejb73",
        name: "EJB 73",
        internalLength: 600,
        internalWidth: 530,
        internalDepth: 410,
        mountingPlate: { x: 650, y: 410 },
        maxHolesLong: 40,
        maxHolesShort: 16,
        railCount: 3,
        maxTerminals: 110
    },
    {
        id: "ejb91",
        name: "EJB 91",
        internalLength: 700,
        internalWidth: 650,
        internalDepth: 510,
        mountingPlate: { x: 750, y: 440 },
        maxHolesLong: 112,
        maxHolesShort: 70,
        railCount: 3,
        maxTerminals: 140
    },
    {
        id: "ejb93",
        name: "EJB 93",
        internalLength: 700,
        internalWidth: 650,
        internalDepth: 510,
        mountingPlate: { x: 750, y: 440 },
        maxHolesLong: 48,
        maxHolesShort: 30,
        railCount: 3,
        maxTerminals: 140
    }
];

export const COMPONENTS = {
    TERMINAL_2_5: {
        name: "UT 2,5 Terminal",
        width: 5.2,
        height: 47.7,
        depth: 47.5,
        color: "#ccc"
    },
    HOLE_M20: {
        name: "M20 Hole",
        diameter: 20,
        clearance: 5 // Minimum gap between holes
    },
    RAIL_DIN: {
        name: "DIN Rail NS 35",
        height: 35,
        depth: 7.5
    }
};
