import type { BoxModel, HoleSize } from "../types/box-models";
import type { ValidationError, ValidationWarning, ValidationResult, HoleConfig } from "../types/configuration";
import { COMPONENTS, HOLE_SIZES } from "../constants/engineering-data";
import { getSeriesRules, getSeriesForBox } from "../constants/series-rules";

export function getHoleSizeSpec(sizeId: string): HoleSize {
  return HOLE_SIZES.find((h) => h.id === sizeId) ?? HOLE_SIZES[0];
}

export interface HolePlacementResult {
  valid: boolean;
  message: string;
  maxPossible: number;
}

export function validateHolePlacement(
  holeCount: number,
  sideLength: number,
  boxId: string,
  holeSizeId: string = "M20"
): HolePlacementResult {
  if (holeCount === 0) {
    return { valid: true, message: "", maxPossible: 0 };
  }

  const rules = getSeriesRules(getSeriesForBox(boxId));
  const holeSize = getHoleSizeSpec(holeSizeId);

  const availableLength = sideLength - 2 * rules.edgeMargin;
  const spacePerHole = holeSize.diameter + Math.max(rules.holeClearance, holeSize.clearance);
  const maxPossible = Math.floor((availableLength + Math.max(rules.holeClearance, holeSize.clearance)) / spacePerHole);

  if (holeCount > maxPossible) {
    return {
      valid: false,
      message: `Fiziksel olarak en fazla ${maxPossible} adet ${holeSizeId} delik sığar. (Kenar: ${sideLength}mm, Kenar boşluğu: ${rules.edgeMargin}mm)`,
      maxPossible,
    };
  }

  return { valid: true, message: "", maxPossible };
}

export function validateTerminalPlacement(
  terminalCount: number,
  box: BoxModel
): HolePlacementResult {
  const terminalWidth = COMPONENTS.TERMINAL_2_5.width;
  const railMargin = 20;
  const availableRailLength = box.internalWidth - 2 * railMargin;
  const maxPerRail = Math.floor(availableRailLength / terminalWidth);
  const maxTotal = maxPerRail * box.railCount;

  if (terminalCount > maxTotal) {
    return {
      valid: false,
      message: `Ray kapasitesi aşıldı. Fiziksel maksimum: ${maxTotal} klemens.`,
      maxPossible: maxTotal,
    };
  }

  if (terminalCount > box.maxTerminals) {
    return {
      valid: false,
      message: `Kutu kapasitesi aşıldı. Maksimum: ${box.maxTerminals} klemens.`,
      maxPossible: box.maxTerminals,
    };
  }

  return { valid: true, message: "", maxPossible: box.maxTerminals };
}

export interface ConfigForValidation {
  terminals: number;
  holesTop: HoleConfig;
  holesBottom: HoleConfig;
  holesLeft: HoleConfig;
  holesRight: HoleConfig;
}

export function runFullValidation(
  box: BoxModel,
  config: ConfigForValidation
): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  // Hole validations per side
  const sides = [
    { key: "holesTop" as const, length: box.internalWidth, config: config.holesTop },
    { key: "holesBottom" as const, length: box.internalWidth, config: config.holesBottom },
    { key: "holesLeft" as const, length: box.internalLength, config: config.holesLeft },
    { key: "holesRight" as const, length: box.internalLength, config: config.holesRight },
  ];

  for (const side of sides) {
    const result = validateHolePlacement(
      side.config.count,
      side.length,
      box.id,
      side.config.size
    );
    if (!result.valid) {
      errors.push({ field: side.key, message: result.message, maxPossible: result.maxPossible });
    }
  }

  // Terminal validation
  const termResult = validateTerminalPlacement(config.terminals, box);
  if (!termResult.valid) {
    errors.push({ field: "terminals", message: termResult.message, maxPossible: termResult.maxPossible });
  }

  // Capacity warnings
  if (config.terminals > box.maxTerminals * 0.9 && termResult.valid) {
    warnings.push({ field: "terminals", message: "Klemens kapasitesinin %90'ına yaklaştınız." });
  }

  const totalHoles =
    config.holesTop.count + config.holesBottom.count +
    config.holesLeft.count + config.holesRight.count;
  const maxTotalHoles = box.maxHolesLong * 2 + box.maxHolesShort * 2;
  if (totalHoles > maxTotalHoles * 0.9 && errors.length === 0) {
    warnings.push({ field: "holes", message: "Toplam delik kapasitesinin %90'ına yaklaştınız." });
  }

  return { errors, warnings, isValid: errors.length === 0 };
}
