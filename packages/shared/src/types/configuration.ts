export interface HoleConfig {
  count: number;
  size: string;
}

export interface ConfigurationInput {
  boxModelId: string;
  terminals: number;
  holesTop: HoleConfig;
  holesBottom: HoleConfig;
  holesLeft: HoleConfig;
  holesRight: HoleConfig;
  switchgear: SwitchgearPlacement[];
  coverElements: CoverElementPlacement[];
  name?: string;
  notes?: string;
  drawingNumber?: string;
}

export interface SwitchgearPlacement {
  componentId: string;
  railIndex: number;
  quantity: number;
  currentRating?: number;
  coilVoltage?: number;
}

export interface CoverElementPlacement {
  elementId: string;
  x: number;
  y: number;
}

export type ConfigurationStatus =
  | "draft"
  | "submitted"
  | "approved"
  | "production";

export interface SavedConfiguration extends ConfigurationInput {
  id: string;
  userId: string;
  status: ConfigurationStatus;
  drawingNumber: string;
  createdAt: string;
  updatedAt: string;
}

export interface ValidationError {
  field: string;
  message: string;
  maxPossible?: number;
}

export interface ValidationWarning {
  field: string;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface BOMItem {
  partName: string;
  partCode: string;
  quantity: number;
  description: string;
}

export interface BOMResult {
  items: BOMItem[];
  totalParts: number;
}

export interface RailLayout {
  id: string;
  y: number;
  terminalCount: number;
  width: number;
  x: number;
}

export interface HolePosition {
  pos: number;
}

export interface LayoutResult {
  rails: RailLayout[];
  holesTop: HolePosition[];
  holesBottom: HolePosition[];
  holesLeft: HolePosition[];
  holesRight: HolePosition[];
}
