import { create } from "zustand"

import { VesselExcursion } from "@/types/vessel"

interface ITrackModeOptions {
  startDate: Date | undefined
  endDate: Date | undefined
  trackedVesselIDs: string[]
  excursions: { [vesselID: string]: VesselExcursion[] }
  vesselsIDsHidden: string[]
  excursionsIDsHidden: string[]
  focusedExcursionID: string | null
  showPositions: boolean
  segmentMode: "speed" | "vessel"
}

interface ITrackModeOptionsActions {
  setStartDate: (startDate: Date | undefined) => void
  setEndDate: (endDate: Date | undefined) => void

  // Tracked vessels
  setTrackedVesselIDs: (trackedVesselIDs: string[]) => void
  addTrackedVessel: (vesselID: string) => void
  removeTrackedVessel: (vesselID: string) => void
  clearTrackedVessels: () => void
  setVesselVisibility: (vesselID: string, visible: boolean) => void
  toggleVesselVisibility: (vesselID: string) => void

  // Excursions
  setExcursions: (excursions: { [vesselID: string]: VesselExcursion[] }) => void
  setVesselExcursions: (vesselID: string, excursions: VesselExcursion[]) => void
  removeVesselExcursions: (vesselID: string, excursionID: string) => void
  clearExcursions: () => void
  setExcursionVisibility: (excursionID: string, visible: boolean) => void
  toggleExcursionVisibility: (excursionID: string) => void
  setFocusedExcursionID: (excursionID: string | null) => void

  // Settings
  setShowPositions: (showPositions: boolean) => void
  setSegmentMode: (segmentMode: "speed" | "vessel") => void
}

type ITrackModeOptionsStore = ITrackModeOptions & ITrackModeOptionsActions

const defaultInitState: ITrackModeOptions = {
  startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
  endDate: new Date(),
  trackedVesselIDs: [],
  excursions: {},
  vesselsIDsHidden: [],
  excursionsIDsHidden: [],
  focusedExcursionID: null,
  showPositions: false,
  segmentMode: "vessel",
}

export const useTrackModeOptionsStore = create<ITrackModeOptionsStore>()(
  (set) => ({
    ...defaultInitState,

    setStartDate: (startDate) => set((state) => ({ ...state, startDate })),
    setEndDate: (endDate) => set((state) => ({ ...state, endDate })),

    setTrackedVesselIDs: (trackedVesselIDs) =>
      set((state) => ({ ...state, trackedVesselIDs })),
    addTrackedVessel: (vesselID) =>
      set((state) => ({
        ...state,
        trackedVesselIDs: [...state.trackedVesselIDs, vesselID],
      })),
    removeTrackedVessel: (vesselID) =>
      set((state) => ({
        ...state,
        trackedVesselIDs: state.trackedVesselIDs.filter(
          (id) => id !== vesselID
        ),
      })),
    clearTrackedVessels: () =>
      set((state) => ({ ...state, trackedVesselIDs: [] })),
    setVesselVisibility: (vesselID, visible) =>
      set((state) => ({
        ...state,
        vesselsIDsHidden: visible
          ? state.vesselsIDsHidden.filter((id) => id !== vesselID)
          : [...state.vesselsIDsHidden, vesselID],
      })),
    toggleVesselVisibility: (vesselID) =>
      set((state) => ({
        ...state,
        vesselsIDsHidden: state.vesselsIDsHidden.includes(vesselID)
          ? state.vesselsIDsHidden.filter((id) => id !== vesselID)
          : [...state.vesselsIDsHidden, vesselID],
      })),

    setExcursions: (excursions) => set((state) => ({ ...state, excursions })),
    setVesselExcursions: (vesselID, excursions) =>
      set((state) => ({
        ...state,
        excursions: {
          ...state.excursions,
          [vesselID]: excursions,
        },
      })),
    removeVesselExcursions: (vesselID, excursionID) =>
      set((state) => ({
        ...state,
        excursions: {
          ...state.excursions,
          [vesselID]: state.excursions[vesselID].filter(
            (excursion) => excursion.excursion_id !== excursionID
          ),
        },
      })),
    clearExcursions: () => set((state) => ({ ...state, excursions: {} })),
    setExcursionVisibility: (excursionID, visible) =>
      set((state) => ({
        ...state,
        excursionsIDsHidden: visible
          ? state.excursionsIDsHidden.filter((excursion_id) => excursion_id !== excursionID)
          : [...state.excursionsIDsHidden, excursionID],
      })),
    toggleExcursionVisibility: (excursionID) =>
      set((state) => ({
        ...state,
        excursionsIDsHidden: state.excursionsIDsHidden.includes(excursionID)
          ? state.excursionsIDsHidden.filter((excursion_id) => excursion_id !== excursionID)
          : [...state.excursionsIDsHidden, excursionID],
      })),
    setFocusedExcursionID: (excursionID) =>
      set((state) => ({ ...state, focusedExcursionID: excursionID })),

    setShowPositions: (showPositions) =>
      set((state) => ({ ...state, showPositions })),
    setSegmentMode: (segmentMode) =>
      set((state) => ({ ...state, segmentMode })),
  })
)
