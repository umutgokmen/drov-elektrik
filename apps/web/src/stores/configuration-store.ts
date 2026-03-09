import { create } from "zustand";

export interface HoleConfig {
  count: number;
  size: string; // M20, M25, M32, M40, M50
}

export interface SwitchgearItem {
  componentId: string;
  railIndex: number;
  quantity: number;
  currentRating?: number;
  coilVoltage?: number;
}

export interface CoverElement {
  elementId: string;
  x: number;
  y: number;
}

export interface ConfigurationState {
  // Box selection
  selectedBoxId: string | null;
  selectedSeries: string;

  // Terminal config
  terminals: number;

  // Hole config (per side)
  holesTop: HoleConfig;
  holesBottom: HoleConfig;
  holesLeft: HoleConfig;
  holesRight: HoleConfig;

  // Switchgear
  switchgearItems: SwitchgearItem[];

  // Cover elements
  coverElements: CoverElement[];

  // Metadata
  configName: string;
  notes: string;
  drawingNumber: string;

  // View state
  activeView: "2d" | "3d" | "cover";

  // Actions
  setSelectedBox: (boxId: string) => void;
  setSelectedSeries: (series: string) => void;
  setTerminals: (count: number) => void;
  setHoles: (
    side: "top" | "bottom" | "left" | "right",
    config: HoleConfig
  ) => void;
  addSwitchgearItem: (item: SwitchgearItem) => void;
  removeSwitchgearItem: (index: number) => void;
  addCoverElement: (element: CoverElement) => void;
  removeCoverElement: (index: number) => void;
  updateCoverElement: (index: number, element: Partial<CoverElement>) => void;
  setConfigName: (name: string) => void;
  setNotes: (notes: string) => void;
  setActiveView: (view: "2d" | "3d" | "cover") => void;
  resetConfiguration: () => void;
  loadConfiguration: (config: Partial<ConfigurationState>) => void;
}

const defaultHoleConfig: HoleConfig = { count: 0, size: "M20" };

const initialState = {
  selectedBoxId: null,
  selectedSeries: "ejb",
  terminals: 0,
  holesTop: { ...defaultHoleConfig },
  holesBottom: { ...defaultHoleConfig },
  holesLeft: { ...defaultHoleConfig },
  holesRight: { ...defaultHoleConfig },
  switchgearItems: [],
  coverElements: [],
  configName: "",
  notes: "",
  drawingNumber: "",
  activeView: "2d" as const,
};

export const useConfigurationStore = create<ConfigurationState>((set) => ({
  ...initialState,

  setSelectedBox: (boxId) => set({ selectedBoxId: boxId }),
  setSelectedSeries: (series) =>
    set({ selectedSeries: series, selectedBoxId: null }),
  setTerminals: (count) => set({ terminals: count }),
  setHoles: (side, config) => {
    const key = `holes${side.charAt(0).toUpperCase() + side.slice(1)}` as
      | "holesTop"
      | "holesBottom"
      | "holesLeft"
      | "holesRight";
    set({ [key]: config });
  },
  addSwitchgearItem: (item) =>
    set((state) => ({
      switchgearItems: [...state.switchgearItems, item],
    })),
  removeSwitchgearItem: (index) =>
    set((state) => ({
      switchgearItems: state.switchgearItems.filter((_, i) => i !== index),
    })),
  addCoverElement: (element) =>
    set((state) => ({
      coverElements: [...state.coverElements, element],
    })),
  removeCoverElement: (index) =>
    set((state) => ({
      coverElements: state.coverElements.filter((_, i) => i !== index),
    })),
  updateCoverElement: (index, update) =>
    set((state) => ({
      coverElements: state.coverElements.map((el, i) =>
        i === index ? { ...el, ...update } : el
      ),
    })),
  setConfigName: (name) => set({ configName: name }),
  setNotes: (notes) => set({ notes }),
  setActiveView: (view) => set({ activeView: view }),
  resetConfiguration: () => set(initialState),
  loadConfiguration: (config) => set(config),
}));
