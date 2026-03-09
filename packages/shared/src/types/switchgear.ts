export type SwitchgearCategory =
  | "fuse"
  | "mcb"
  | "relay"
  | "contactor"
  | "switch"
  | "terminal"
  | "surge_protector"
  | "timer"
  | "power_supply";

export interface SwitchgearComponent {
  id: string;
  name: string;
  category: SwitchgearCategory;
  brand: string;
  dinModules: number;
  width: number;
  height: number;
  depth: number;
  currentRating?: number[];
  coilVoltage?: number[];
  contactCount?: number;
  poleCount: number;
  mounting: "din_rail";
  crossSection?: number;
  outputVoltage?: number;
  outputCurrent?: number;
  positions?: number;
}

export type CoverElementCategory =
  | "pushbutton"
  | "selector_switch"
  | "indicator_lamp"
  | "emergency_stop"
  | "ammeter"
  | "voltmeter";

export interface CoverElementSpec {
  id: string;
  name: string;
  category: CoverElementCategory;
  cutoutDiameter?: number;
  bezelDiameter?: number;
  cutoutWidth?: number;
  cutoutHeight?: number;
  bezelWidth?: number;
  bezelHeight?: number;
  depthBehindPanel: number;
  color: string;
  function?: string;
  voltage?: number[];
  positions?: number;
}

export interface SaltMalzemeItem {
  partName: string;
  partCode: string;
  quantity: number;
  description: string;
}
