"use client";

import { useQuery } from "@tanstack/react-query";
import { createClient } from "@/lib/supabase/client";
import {
  BOX_MODELS,
  BOX_SERIES,
  HOLE_SIZES,
  SWITCHGEAR_CATALOG,
  COVER_ELEMENTS_CATALOG,
  SALT_MALZEME,
  type BoxModel,
  type BoxSeries,
  type BoxSeriesId,
  type HoleSize,
  type SwitchgearComponent,
  type CoverElementSpec,
  type SaltMalzemeItem,
} from "@drov/shared";

// Fallback to local constants if Supabase is not available
// This makes the app work offline and during development

export function useBoxSeries() {
  const supabase = createClient();

  return useQuery<BoxSeries[]>({
    queryKey: ["box-series"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("box_series")
        .select("*")
        .order("id");

      if (error || !data || data.length === 0) {
        return BOX_SERIES;
      }

      return data.map((s: Record<string, unknown>): BoxSeries => ({
        id: s.id as BoxSeriesId,
        name: s.name as string,
        description: s.description as string,
        edgeMargin: s.edge_margin as number,
        holeClearance: s.hole_clearance as number,
        defaultHoleDiameter: s.default_hole_diameter as number,
        maxHoleDiameter: s.max_hole_diameter as number | undefined,
      }));
    },
    initialData: BOX_SERIES,
  });
}

export function useBoxModels(seriesId?: string) {
  const supabase = createClient();

  return useQuery<BoxModel[]>({
    queryKey: ["box-models", seriesId],
    queryFn: async () => {
      let query = supabase.from("box_models").select("*").order("name");
      if (seriesId) {
        query = query.eq("series_id", seriesId);
      }

      const { data, error } = await query;

      if (error || !data || data.length === 0) {
        const local = seriesId
          ? BOX_MODELS.filter((b) => b.seriesId === seriesId)
          : BOX_MODELS;
        return local;
      }

      return data.map((b: Record<string, unknown>): BoxModel => ({
        id: b.id as string,
        name: b.name as string,
        seriesId: b.series_id as BoxSeriesId,
        internalLength: b.internal_length as number,
        internalWidth: b.internal_width as number,
        internalDepth: b.internal_depth as number,
        mountingPlateX: b.mounting_plate_x as number,
        mountingPlateY: b.mounting_plate_y as number,
        maxHolesLong: b.max_holes_long as number,
        maxHolesShort: b.max_holes_short as number,
        railCount: b.rail_count as number,
        maxTerminals: b.max_terminals as number,
        ipRating: b.ip_rating as string | undefined,
        hasEarthPlate: b.has_earth_plate as boolean | undefined,
      }));
    },
    initialData: seriesId
      ? BOX_MODELS.filter((b) => b.seriesId === seriesId)
      : BOX_MODELS,
  });
}

export function useHoleSizes() {
  const supabase = createClient();

  return useQuery<HoleSize[]>({
    queryKey: ["hole-sizes"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("hole_sizes")
        .select("*")
        .order("diameter");

      if (error || !data || data.length === 0) {
        return HOLE_SIZES;
      }

      return data.map((h: Record<string, unknown>) => ({
        id: h.id as string,
        diameter: h.diameter as number,
        clearance: h.clearance as number,
        name: h.name as string,
        code: h.code as string,
      }));
    },
    initialData: HOLE_SIZES,
  });
}

export function useSwitchgearCatalog() {
  return useQuery<SwitchgearComponent[]>({
    queryKey: ["switchgear-catalog"],
    queryFn: async () => SWITCHGEAR_CATALOG,
    initialData: SWITCHGEAR_CATALOG,
  });
}

export function useCoverElementsCatalog() {
  return useQuery<CoverElementSpec[]>({
    queryKey: ["cover-elements-catalog"],
    queryFn: async () => COVER_ELEMENTS_CATALOG,
    initialData: COVER_ELEMENTS_CATALOG,
  });
}

export function useSaltMalzeme() {
  return useQuery<SaltMalzemeItem[]>({
    queryKey: ["salt-malzeme"],
    queryFn: async () => SALT_MALZEME,
    initialData: SALT_MALZEME,
  });
}
