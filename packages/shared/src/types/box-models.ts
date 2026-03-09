export type BoxSeriesId = "ejb" | "esp" | "esa" | "esx" | "ejbx" | "ejc";

export interface BoxSeries {
  id: BoxSeriesId;
  name: string;
  description: string;
  edgeMargin: number;
  holeClearance: number;
  defaultHoleDiameter: number;
  maxHoleDiameter?: number;
}

export interface BoxModel {
  id: string;
  name: string;
  seriesId: BoxSeriesId;
  internalLength: number;
  internalWidth: number;
  internalDepth: number;
  mountingPlateX: number;
  mountingPlateY: number;
  maxHolesLong: number;
  maxHolesShort: number;
  railCount: number;
  maxTerminals: number;
  ipRating?: string;
  hasEarthPlate?: boolean;
}

export interface HoleSize {
  id: string;
  diameter: number;
  clearance: number;
  name: string;
  code: string;
}
