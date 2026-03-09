"use client";

import { useMemo } from "react";
import { useConfigurationStore } from "@/stores/configuration-store";
import {
  BOX_MODELS,
  BOX_SERIES,
  runFullValidation,
  calculateLayout,
  calculateHolePositions,
  type BoxModel,
  type ValidationResult,
  type RailLayout,
  type HolePosition,
} from "@drov/shared";

export function useConfiguration() {
  const store = useConfigurationStore();

  const selectedBox: BoxModel | null = useMemo(() => {
    if (!store.selectedBoxId) return null;
    return BOX_MODELS.find((b) => b.id === store.selectedBoxId) ?? null;
  }, [store.selectedBoxId]);

  const seriesModels = useMemo(() => {
    return BOX_MODELS.filter((b) => b.seriesId === store.selectedSeries);
  }, [store.selectedSeries]);

  const validation: ValidationResult | null = useMemo(() => {
    if (!selectedBox) return null;
    return runFullValidation(selectedBox, {
      terminals: store.terminals,
      holesTop: store.holesTop,
      holesBottom: store.holesBottom,
      holesLeft: store.holesLeft,
      holesRight: store.holesRight,
    });
  }, [selectedBox, store.terminals, store.holesTop, store.holesBottom, store.holesLeft, store.holesRight]);

  const layout: { rails: RailLayout[]; holesTop: HolePosition[]; holesBottom: HolePosition[]; holesLeft: HolePosition[]; holesRight: HolePosition[] } | null = useMemo(() => {
    if (!selectedBox) return null;
    const rails = calculateLayout(selectedBox, store.terminals);
    const holesTop = calculateHolePositions(store.holesTop.count, selectedBox.internalWidth, store.holesTop.size, selectedBox.id);
    const holesBottom = calculateHolePositions(store.holesBottom.count, selectedBox.internalWidth, store.holesBottom.size, selectedBox.id);
    const holesLeft = calculateHolePositions(store.holesLeft.count, selectedBox.internalLength, store.holesLeft.size, selectedBox.id);
    const holesRight = calculateHolePositions(store.holesRight.count, selectedBox.internalLength, store.holesRight.size, selectedBox.id);
    return { rails, holesTop, holesBottom, holesLeft, holesRight };
  }, [selectedBox, store.terminals, store.holesTop, store.holesBottom, store.holesLeft, store.holesRight]);

  return {
    ...store,
    selectedBox,
    seriesModels,
    series: BOX_SERIES,
    validation,
    layout,
  };
}
