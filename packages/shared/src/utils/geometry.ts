import type { BoxModel } from "../types/box-models";
import type { RailLayout, HolePosition } from "../types/configuration";
import { getSeriesRules, getSeriesForBox } from "../constants/series-rules";
import { getHoleSizeSpec } from "./validation";

export function calculateHolePositions(
  count: number,
  sideLength: number,
  holeSizeId: string = "M20",
  boxId: string = "ejb21"
): HolePosition[] {
  if (count <= 0) return [];

  const holeSize = getHoleSizeSpec(holeSizeId);
  const rules = getSeriesRules(getSeriesForBox(boxId));
  const margin = rules.edgeMargin;

  const totalInternalSpace = sideLength - 2 * margin;
  const spacing = totalInternalSpace / (count + 1);

  return Array.from({ length: count }, (_, i) => ({
    pos: margin + (i + 1) * spacing,
  }));
}

export function calculateLayout(
  box: BoxModel,
  terminalCount: number
): RailLayout[] {
  const rails: RailLayout[] = [];
  const terminalsPerRail = Math.ceil(terminalCount / box.railCount);

  const verticalMargin = 30;
  const availableHeight = box.internalLength - 2 * verticalMargin;
  const railSpacing = box.railCount > 1 ? availableHeight / (box.railCount - 1) : 0;

  for (let i = 0; i < box.railCount; i++) {
    const y =
      box.railCount > 1
        ? verticalMargin + i * railSpacing
        : box.internalLength / 2;

    const countOnThisRail =
      i === box.railCount - 1
        ? terminalCount - i * terminalsPerRail
        : terminalsPerRail;

    rails.push({
      id: `rail-${i}`,
      y,
      terminalCount: Math.max(0, countOnThisRail),
      width: box.internalWidth - 40,
      x: 20,
    });
  }

  return rails;
}
