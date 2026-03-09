import type { BoxSeriesId, BoxSeries } from "../types/box-models";
import { BOX_SERIES } from "./engineering-data";

export interface SeriesRules {
  edgeMargin: number;
  holeClearance: number;
  defaultHoleDiameter: number;
  maxHoleDiameter?: number;
}

export function getSeriesRules(seriesId: BoxSeriesId): SeriesRules {
  const series = BOX_SERIES.find((s) => s.id === seriesId);
  if (!series) {
    return { edgeMargin: 15, holeClearance: 5, defaultHoleDiameter: 20 };
  }
  return {
    edgeMargin: series.edgeMargin,
    holeClearance: series.holeClearance,
    defaultHoleDiameter: series.defaultHoleDiameter,
    maxHoleDiameter: series.maxHoleDiameter,
  };
}

export function getSeriesById(seriesId: BoxSeriesId): BoxSeries | undefined {
  return BOX_SERIES.find((s) => s.id === seriesId);
}

export function getSeriesForBox(boxId: string): BoxSeriesId {
  if (boxId.startsWith("ejbx")) return "ejbx";
  if (boxId.startsWith("ejb")) return "ejb";
  if (boxId.startsWith("ejc")) return "ejc";
  if (boxId.startsWith("esp")) return "esp";
  if (boxId.startsWith("esa")) return "esa";
  if (boxId.startsWith("esx")) return "esx";
  return "ejb";
}
