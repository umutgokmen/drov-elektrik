import type { BoxModel, BoxSeries, HoleSize } from "../types/box-models";
import type { SwitchgearComponent, CoverElementSpec, SaltMalzemeItem } from "../types/switchgear";

// ==================== BOX SERIES ====================

export const BOX_SERIES: BoxSeries[] = [
  { id: "ejb", name: "EJB", description: "Ex-proof Junction Box", edgeMargin: 15, holeClearance: 5, defaultHoleDiameter: 20 },
  { id: "esp", name: "ESP", description: "Ex-proof Small Panel", edgeMargin: 12, holeClearance: 4, defaultHoleDiameter: 20 },
  { id: "esa", name: "ESA", description: "Ex-proof Standard Assembly", edgeMargin: 15, holeClearance: 5, defaultHoleDiameter: 20 },
  { id: "esx", name: "ESX", description: "Ex-proof Stainless Steel", edgeMargin: 20, holeClearance: 8, defaultHoleDiameter: 20 },
  { id: "ejbx", name: "EJBX", description: "Ex-proof Junction Box Extended", edgeMargin: 25, holeClearance: 25, defaultHoleDiameter: 20 },
  { id: "ejc", name: "EJC", description: "Ex-proof Junction Compact (IP66)", edgeMargin: 20, holeClearance: 8, defaultHoleDiameter: 20, maxHoleDiameter: 25 },
];

// ==================== BOX MODELS ====================

export const BOX_MODELS: BoxModel[] = [
  // EJB Series
  { id: "ejb21", name: "EJB 21", seriesId: "ejb", internalLength: 169, internalWidth: 179, internalDepth: 160, mountingPlateX: 180, mountingPlateY: 140, maxHolesLong: 10, maxHolesShort: 8, railCount: 1, maxTerminals: 30 },
  { id: "ejb31", name: "EJB 31", seriesId: "ejb", internalLength: 249, internalWidth: 258, internalDepth: 294, mountingPlateX: 325, mountingPlateY: 225, maxHolesLong: 28, maxHolesShort: 20, railCount: 2, maxTerminals: 52 },
  { id: "ejb51", name: "EJB 51", seriesId: "ejb", internalLength: 390, internalWidth: 388, internalDepth: 370, mountingPlateX: 460, mountingPlateY: 260, maxHolesLong: 44, maxHolesShort: 24, railCount: 2, maxTerminals: 80 },
  { id: "ejb61", name: "EJB 61", seriesId: "ejb", internalLength: 500, internalWidth: 470, internalDepth: 360, mountingPlateX: 560, mountingPlateY: 360, maxHolesLong: 72, maxHolesShort: 48, railCount: 3, maxTerminals: 92 },
  { id: "ejb63", name: "EJB 63", seriesId: "ejb", internalLength: 500, internalWidth: 470, internalDepth: 360, mountingPlateX: 560, mountingPlateY: 360, maxHolesLong: 36, maxHolesShort: 24, railCount: 3, maxTerminals: 92 },
  { id: "ejb71", name: "EJB 71", seriesId: "ejb", internalLength: 600, internalWidth: 530, internalDepth: 410, mountingPlateX: 650, mountingPlateY: 410, maxHolesLong: 90, maxHolesShort: 59, railCount: 3, maxTerminals: 110 },
  { id: "ejb73", name: "EJB 73", seriesId: "ejb", internalLength: 600, internalWidth: 530, internalDepth: 410, mountingPlateX: 650, mountingPlateY: 410, maxHolesLong: 40, maxHolesShort: 16, railCount: 3, maxTerminals: 110 },
  { id: "ejb91", name: "EJB 91", seriesId: "ejb", internalLength: 700, internalWidth: 650, internalDepth: 510, mountingPlateX: 750, mountingPlateY: 440, maxHolesLong: 112, maxHolesShort: 70, railCount: 3, maxTerminals: 140 },
  { id: "ejb93", name: "EJB 93", seriesId: "ejb", internalLength: 700, internalWidth: 650, internalDepth: 510, mountingPlateX: 750, mountingPlateY: 440, maxHolesLong: 48, maxHolesShort: 30, railCount: 3, maxTerminals: 140 },

  // ESP Series
  { id: "esp1", name: "ESP 1", seriesId: "esp", internalLength: 120, internalWidth: 80, internalDepth: 60, mountingPlateX: 100, mountingPlateY: 60, maxHolesLong: 3, maxHolesShort: 2, railCount: 1, maxTerminals: 7 },
  { id: "esp2", name: "ESP 2", seriesId: "esp", internalLength: 150, internalWidth: 100, internalDepth: 80, mountingPlateX: 130, mountingPlateY: 80, maxHolesLong: 4, maxHolesShort: 3, railCount: 1, maxTerminals: 11 },
  { id: "esp3", name: "ESP 3", seriesId: "esp", internalLength: 200, internalWidth: 150, internalDepth: 100, mountingPlateX: 180, mountingPlateY: 110, maxHolesLong: 7, maxHolesShort: 5, railCount: 1, maxTerminals: 21 },
  { id: "esp4", name: "ESP 4", seriesId: "esp", internalLength: 300, internalWidth: 200, internalDepth: 120, mountingPlateX: 280, mountingPlateY: 160, maxHolesLong: 11, maxHolesShort: 7, railCount: 2, maxTerminals: 40 },
  { id: "esp5", name: "ESP 5", seriesId: "esp", internalLength: 400, internalWidth: 300, internalDepth: 150, mountingPlateX: 380, mountingPlateY: 240, maxHolesLong: 15, maxHolesShort: 11, railCount: 2, maxTerminals: 60 },

  // ESA Series
  { id: "esa1", name: "ESA 1", seriesId: "esa", internalLength: 300, internalWidth: 300, internalDepth: 180, mountingPlateX: 340, mountingPlateY: 220, maxHolesLong: 14, maxHolesShort: 14, railCount: 2, maxTerminals: 50 },
  { id: "esa2", name: "ESA 2", seriesId: "esa", internalLength: 400, internalWidth: 350, internalDepth: 200, mountingPlateX: 440, mountingPlateY: 260, maxHolesLong: 22, maxHolesShort: 18, railCount: 2, maxTerminals: 70 },
  { id: "esa3", name: "ESA 3", seriesId: "esa", internalLength: 250, internalWidth: 200, internalDepth: 150, mountingPlateX: 270, mountingPlateY: 220, maxHolesLong: 18, maxHolesShort: 12, railCount: 1, maxTerminals: 28 },
  { id: "esa4", name: "ESA 4", seriesId: "esa", internalLength: 350, internalWidth: 300, internalDepth: 200, mountingPlateX: 370, mountingPlateY: 320, maxHolesLong: 24, maxHolesShort: 20, railCount: 2, maxTerminals: 52 },
  { id: "esa5", name: "ESA 5", seriesId: "esa", internalLength: 450, internalWidth: 400, internalDepth: 250, mountingPlateX: 470, mountingPlateY: 420, maxHolesLong: 32, maxHolesShort: 28, railCount: 2, maxTerminals: 76 },
  { id: "esa6", name: "ESA 6", seriesId: "esa", internalLength: 550, internalWidth: 450, internalDepth: 300, mountingPlateX: 570, mountingPlateY: 470, maxHolesLong: 42, maxHolesShort: 32, railCount: 3, maxTerminals: 96 },

  // ESX Series
  { id: "esx1", name: "ESX 1", seriesId: "esx", internalLength: 400, internalWidth: 400, internalDepth: 220, mountingPlateX: 440, mountingPlateY: 280, maxHolesLong: 22, maxHolesShort: 22, railCount: 2, maxTerminals: 60 },
  { id: "esx2", name: "ESX 2", seriesId: "esx", internalLength: 500, internalWidth: 450, internalDepth: 250, mountingPlateX: 550, mountingPlateY: 320, maxHolesLong: 30, maxHolesShort: 26, railCount: 3, maxTerminals: 90 },
  { id: "esx15", name: "ESX 15", seriesId: "esx", internalLength: 150, internalWidth: 150, internalDepth: 80, mountingPlateX: 130, mountingPlateY: 130, maxHolesLong: 4, maxHolesShort: 4, railCount: 1, maxTerminals: 16 },
  { id: "esx20", name: "ESX 20", seriesId: "esx", internalLength: 200, internalWidth: 200, internalDepth: 100, mountingPlateX: 180, mountingPlateY: 180, maxHolesLong: 6, maxHolesShort: 6, railCount: 1, maxTerminals: 24 },
  { id: "esx30", name: "ESX 30", seriesId: "esx", internalLength: 300, internalWidth: 250, internalDepth: 150, mountingPlateX: 280, mountingPlateY: 230, maxHolesLong: 8, maxHolesShort: 6, railCount: 2, maxTerminals: 40 },
  { id: "esx40", name: "ESX 40", seriesId: "esx", internalLength: 400, internalWidth: 300, internalDepth: 200, mountingPlateX: 380, mountingPlateY: 280, maxHolesLong: 10, maxHolesShort: 8, railCount: 2, maxTerminals: 56 },

  // EJBX Series
  { id: "ejbx1", name: "EJBX 1", seriesId: "ejbx", internalLength: 200, internalWidth: 160, internalDepth: 120, mountingPlateX: 240, mountingPlateY: 180, maxHolesLong: 8, maxHolesShort: 6, railCount: 1, maxTerminals: 20 },
  { id: "ejbx2", name: "EJBX 2", seriesId: "ejbx", internalLength: 300, internalWidth: 230, internalDepth: 150, mountingPlateX: 340, mountingPlateY: 260, maxHolesLong: 16, maxHolesShort: 10, railCount: 2, maxTerminals: 40 },
  { id: "ejbx3", name: "EJBX 3", seriesId: "ejbx", internalLength: 400, internalWidth: 310, internalDepth: 200, mountingPlateX: 450, mountingPlateY: 340, maxHolesLong: 24, maxHolesShort: 14, railCount: 2, maxTerminals: 60 },
  { id: "ejbx4", name: "EJBX 4", seriesId: "ejbx", internalLength: 500, internalWidth: 400, internalDepth: 250, mountingPlateX: 560, mountingPlateY: 440, maxHolesLong: 32, maxHolesShort: 18, railCount: 3, maxTerminals: 80 },

  // EJC Series
  { id: "ejc01", name: "EJC 01", seriesId: "ejc", internalLength: 150, internalWidth: 150, internalDepth: 80, mountingPlateX: 160, mountingPlateY: 160, maxHolesLong: 4, maxHolesShort: 4, railCount: 1, maxTerminals: 16, ipRating: "IP66", hasEarthPlate: true },
  { id: "ejc02", name: "EJC 02", seriesId: "ejc", internalLength: 200, internalWidth: 150, internalDepth: 80, mountingPlateX: 210, mountingPlateY: 160, maxHolesLong: 6, maxHolesShort: 4, railCount: 1, maxTerminals: 24, ipRating: "IP66", hasEarthPlate: true },
  { id: "ejc03", name: "EJC 03", seriesId: "ejc", internalLength: 200, internalWidth: 200, internalDepth: 100, mountingPlateX: 210, mountingPlateY: 210, maxHolesLong: 6, maxHolesShort: 6, railCount: 1, maxTerminals: 30, ipRating: "IP66", hasEarthPlate: true },
  { id: "ejc04", name: "EJC 04", seriesId: "ejc", internalLength: 300, internalWidth: 200, internalDepth: 120, mountingPlateX: 310, mountingPlateY: 210, maxHolesLong: 10, maxHolesShort: 6, railCount: 2, maxTerminals: 50, ipRating: "IP66", hasEarthPlate: true },
];

// ==================== HOLE SIZES ====================

export const HOLE_SIZES: HoleSize[] = [
  { id: "M20", diameter: 20, clearance: 5, name: "M20 Kablo Rakoru", code: "M20-GL" },
  { id: "M25", diameter: 25, clearance: 6, name: "M25 Kablo Rakoru", code: "M25-GL" },
  { id: "M32", diameter: 32, clearance: 8, name: "M32 Kablo Rakoru", code: "M32-GL" },
  { id: "M40", diameter: 40, clearance: 10, name: "M40 Kablo Rakoru", code: "M40-GL" },
  { id: "M50", diameter: 50, clearance: 12, name: "M50 Kablo Rakoru", code: "M50-GL" },
];

// ==================== COMPONENTS ====================

export const COMPONENTS = {
  TERMINAL_2_5: { name: "UT 2,5 Terminal", width: 5.2, height: 47.7, depth: 47.5 },
  HOLE_M20: { name: "M20 Delik", diameter: 20, clearance: 5 },
  RAIL_DIN: { name: "DIN Ray NS 35", height: 35, depth: 7.5 },
} as const;

export const DIN_MODULE_WIDTH = 17.5;

// ==================== SWITCHGEAR CATALOG ====================

export const SWITCHGEAR_CATALOG: SwitchgearComponent[] = [
  { id: "fuse-nh00", name: "NH00 Sigorta Yuvası", category: "fuse", brand: "Generic", dinModules: 3, width: 52.5, height: 70, depth: 62, currentRating: [16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160], poleCount: 3, mounting: "din_rail" },
  { id: "fuse-nh1", name: "NH1 Sigorta Yuvası", category: "fuse", brand: "Generic", dinModules: 3, width: 52.5, height: 70, depth: 70, currentRating: [63, 80, 100, 125, 160, 200, 250], poleCount: 3, mounting: "din_rail" },
  { id: "mcb-1p", name: "Otomatik Sigorta 1P", category: "mcb", brand: "Generic", dinModules: 1, width: 17.5, height: 80, depth: 68, currentRating: [6, 10, 16, 20, 25, 32, 40, 50, 63], poleCount: 1, mounting: "din_rail" },
  { id: "mcb-2p", name: "Otomatik Sigorta 2P", category: "mcb", brand: "Generic", dinModules: 2, width: 35.0, height: 80, depth: 68, currentRating: [6, 10, 16, 20, 25, 32, 40, 50, 63], poleCount: 2, mounting: "din_rail" },
  { id: "mcb-3p", name: "Otomatik Sigorta 3P", category: "mcb", brand: "Generic", dinModules: 3, width: 52.5, height: 80, depth: 68, currentRating: [6, 10, 16, 20, 25, 32, 40, 50, 63], poleCount: 3, mounting: "din_rail" },
  { id: "mcb-4p", name: "Otomatik Sigorta 4P", category: "mcb", brand: "Generic", dinModules: 4, width: 70.0, height: 80, depth: 68, currentRating: [6, 10, 16, 20, 25, 32, 40, 50, 63], poleCount: 4, mounting: "din_rail" },
  { id: "relay-4co", name: "Ara Röle 4CO", category: "relay", brand: "Generic", dinModules: 1, width: 17.5, height: 80, depth: 62, coilVoltage: [24, 48, 110, 230], contactCount: 4, poleCount: 1, mounting: "din_rail" },
  { id: "relay-2co", name: "Ara Röle 2CO", category: "relay", brand: "Generic", dinModules: 1, width: 15.5, height: 80, depth: 62, coilVoltage: [24, 48, 110, 230], contactCount: 2, poleCount: 1, mounting: "din_rail" },
  { id: "contactor-9a", name: "Kontaktör 9A", category: "contactor", brand: "Generic", dinModules: 3, width: 45, height: 82, depth: 77, currentRating: [9], coilVoltage: [24, 48, 110, 230], poleCount: 3, mounting: "din_rail" },
  { id: "contactor-18a", name: "Kontaktör 18A", category: "contactor", brand: "Generic", dinModules: 3, width: 45, height: 82, depth: 77, currentRating: [18], coilVoltage: [24, 48, 110, 230], poleCount: 3, mounting: "din_rail" },
  { id: "contactor-32a", name: "Kontaktör 32A", category: "contactor", brand: "Generic", dinModules: 3, width: 55, height: 95, depth: 85, currentRating: [32], coilVoltage: [24, 48, 110, 230], poleCount: 3, mounting: "din_rail" },
  { id: "switch-isolator-3p", name: "Yük Ayırıcı 3P", category: "switch", brand: "Generic", dinModules: 3, width: 52.5, height: 80, depth: 68, currentRating: [25, 32, 40, 63, 80, 100], poleCount: 3, mounting: "din_rail" },
  { id: "terminal-2.5", name: "UT 2,5 Klemens", category: "terminal", brand: "Phoenix Contact", dinModules: 0, width: 5.2, height: 47.7, depth: 47.5, crossSection: 2.5, poleCount: 1, mounting: "din_rail" },
  { id: "terminal-4", name: "UT 4 Klemens", category: "terminal", brand: "Phoenix Contact", dinModules: 0, width: 6.2, height: 47.7, depth: 47.5, crossSection: 4, poleCount: 1, mounting: "din_rail" },
  { id: "terminal-6", name: "UT 6 Klemens", category: "terminal", brand: "Phoenix Contact", dinModules: 0, width: 8.2, height: 52.3, depth: 51.9, crossSection: 6, poleCount: 1, mounting: "din_rail" },
  { id: "surge-type2", name: "Tip 2 Parafudr", category: "surge_protector", brand: "Generic", dinModules: 4, width: 70, height: 90, depth: 65, poleCount: 3, mounting: "din_rail" },
  { id: "timer-digital", name: "Dijital Zaman Rölesi", category: "timer", brand: "Generic", dinModules: 1, width: 17.5, height: 90, depth: 62, coilVoltage: [24, 230], poleCount: 1, mounting: "din_rail" },
  { id: "psu-24v-2.5a", name: "24V 2.5A Güç Kaynağı", category: "power_supply", brand: "Generic", dinModules: 2, width: 35, height: 90, depth: 55, outputVoltage: 24, outputCurrent: 2.5, poleCount: 1, mounting: "din_rail" },
];

// ==================== COVER ELEMENTS CATALOG ====================

export const COVER_ELEMENTS_CATALOG: CoverElementSpec[] = [
  { id: "btn-22-green", name: "Yeşil Buton 22mm", category: "pushbutton", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 40, color: "green", function: "start" },
  { id: "btn-22-red", name: "Kırmızı Buton 22mm", category: "pushbutton", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 40, color: "red", function: "stop" },
  { id: "btn-22-yellow", name: "Sarı Buton 22mm", category: "pushbutton", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 40, color: "yellow", function: "general" },
  { id: "btn-22-blue", name: "Mavi Buton 22mm", category: "pushbutton", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 40, color: "blue", function: "reset" },
  { id: "btn-22-white", name: "Beyaz Buton 22mm", category: "pushbutton", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 40, color: "white", function: "general" },
  { id: "sel-22-2pos", name: "2 Konumlu Anahtar 22mm", category: "selector_switch", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 45, color: "black", positions: 2 },
  { id: "sel-22-3pos", name: "3 Konumlu Anahtar 22mm", category: "selector_switch", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 45, color: "black", positions: 3 },
  { id: "lamp-22-green", name: "Yeşil Sinyal Lambası 22mm", category: "indicator_lamp", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 30, color: "green", voltage: [24, 230] },
  { id: "lamp-22-red", name: "Kırmızı Sinyal Lambası 22mm", category: "indicator_lamp", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 30, color: "red", voltage: [24, 230] },
  { id: "lamp-22-yellow", name: "Sarı Sinyal Lambası 22mm", category: "indicator_lamp", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 30, color: "yellow", voltage: [24, 230] },
  { id: "lamp-22-blue", name: "Mavi Sinyal Lambası 22mm", category: "indicator_lamp", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 30, color: "blue", voltage: [24, 230] },
  { id: "lamp-22-white", name: "Beyaz Sinyal Lambası 22mm", category: "indicator_lamp", cutoutDiameter: 22, bezelDiameter: 30, depthBehindPanel: 30, color: "white", voltage: [24, 230] },
  { id: "estop-40", name: "Acil Stop Butonu 40mm", category: "emergency_stop", cutoutDiameter: 22, bezelDiameter: 40, depthBehindPanel: 50, color: "red", function: "emergency_stop" },
  { id: "ammeter-72", name: "Ampermetre 72x72mm", category: "ammeter", cutoutWidth: 68, cutoutHeight: 68, bezelWidth: 72, bezelHeight: 72, depthBehindPanel: 50, color: "black" },
  { id: "voltmeter-72", name: "Voltmetre 72x72mm", category: "voltmeter", cutoutWidth: 68, cutoutHeight: 68, bezelWidth: 72, bezelHeight: 72, depthBehindPanel: 50, color: "black" },
];

// ==================== SALT MALZEME ====================

export const SALT_MALZEME: SaltMalzemeItem[] = [
  { partName: "EJB Kapak", partCode: "EJB-COVER", quantity: 1, description: "Kutu kapağı" },
  { partName: "CLIPFIX 35/5 Uç Kelepçe", partCode: "pnl_302203_CLIPFIX-35-5", quantity: 2, description: "DIN ray uç kelepçesi (ray başına 2 adet)" },
  { partName: "Drenaj Valfi M20x1.5", partCode: "Drain_Valve_M20x1.5mm", quantity: 1, description: "Kondensasyon drenaj valfi M20x1.5mm" },
];
