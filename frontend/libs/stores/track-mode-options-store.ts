import { create } from "zustand"

import { VesselExcursion } from "@/types/vessel"

interface ITrackModeOptions {
  startDate: Date | undefined
  endDate: Date | undefined
  trackedVesselIDs: number[]
  excursions: { [vesselID: number]: VesselExcursion[] }
  vesselsIDsHidden: number[]
  excursionsIDsHidden: number[]
}

interface ITrackModeOptionsActions {
  setStartDate: (startDate: Date | undefined) => void
  setEndDate: (endDate: Date | undefined) => void

  // Tracked vessels
  setTrackedVesselIDs: (trackedVesselIDs: number[]) => void
  addTrackedVessel: (vesselID: number) => void
  removeTrackedVessel: (vesselID: number) => void
  clearTrackedVessels: () => void
  setVesselVisibility: (vesselID: number, visible: boolean) => void

  // Excursions
  setExcursions: (excursions: { [vesselID: number]: VesselExcursion[] }) => void
  addExcursion: (vesselID: number, excursion: VesselExcursion) => void
  removeExcursion: (vesselID: number, excursionID: number) => void
  clearExcursions: () => void
  setExcursionVisibility: (excursionID: number, visible: boolean) => void
}

type ITrackModeOptionsStore = ITrackModeOptions & ITrackModeOptionsActions

const defaultInitState: ITrackModeOptions = {
  startDate: undefined,
  endDate: undefined,
  trackedVesselIDs: [],
  excursions: {},
  vesselsIDsHidden: [],
  excursionsIDsHidden: [],
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
          ? []
          : state.vesselsIDsHidden.filter((id) => id !== vesselID),
      })),

    setExcursions: (excursions) => set((state) => ({ ...state, excursions })),
    addExcursion: (vesselID, excursion) =>
      set((state) => ({
        ...state,
        excursions: {
          ...state.excursions,
          [vesselID]: [...state.excursions[vesselID], excursion],
        },
      })),
    removeExcursion: (vesselID, excursionID) =>
      set((state) => ({
        ...state,
        excursions: {
          ...state.excursions,
          [vesselID]: state.excursions[vesselID].filter(
            (excursion) => excursion.id !== excursionID
          ),
        },
      })),
    clearExcursions: () => set((state) => ({ ...state, excursions: {} })),
    setExcursionVisibility: (excursionID, visible) =>
      set((state) => ({
        ...state,
        excursionsIDsHidden: visible
          ? []
          : state.excursionsIDsHidden.filter((id) => id !== excursionID),
      })),
  })
)
