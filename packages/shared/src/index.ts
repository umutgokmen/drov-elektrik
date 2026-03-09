// Types
export type { BoxSeriesId, BoxSeries, BoxModel, HoleSize } from "./types/box-models";
export type {
  HoleConfig,
  ConfigurationInput,
  SwitchgearPlacement,
  CoverElementPlacement,
  ConfigurationStatus,
  SavedConfiguration,
  ValidationError,
  ValidationWarning,
  ValidationResult,
  BOMItem,
  BOMResult,
  RailLayout,
  HolePosition,
  LayoutResult,
} from "./types/configuration";
export type {
  SwitchgearCategory,
  SwitchgearComponent,
  CoverElementCategory,
  CoverElementSpec,
  SaltMalzemeItem,
} from "./types/switchgear";

// Constants
export {
  BOX_SERIES,
  BOX_MODELS,
  HOLE_SIZES,
  COMPONENTS,
  DIN_MODULE_WIDTH,
  SWITCHGEAR_CATALOG,
  COVER_ELEMENTS_CATALOG,
  SALT_MALZEME,
} from "./constants/engineering-data";
export { getSeriesRules, getSeriesById, getSeriesForBox } from "./constants/series-rules";

// Utils
export {
  validateHolePlacement,
  validateTerminalPlacement,
  runFullValidation,
  getHoleSizeSpec,
} from "./utils/validation";
export { calculateHolePositions, calculateLayout } from "./utils/geometry";
