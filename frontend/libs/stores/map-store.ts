import { MapViewState } from "@deck.gl/core"
import { createStore } from "zustand/vanilla"

import {
  VesselExcursionSegments,
  VesselPosition,
} from "@/types/vessel"

export interface ViewState {
  longitude: number
  latitude: number
  zoom: number
  pitch?: number
  bearing?: number
  transitionDuration?: number
  transitionInterpolator?: any
}


export interface TrackModeOptions {
  startDate: Date | undefined
  endDate: Date | undefined
  vesselsIDsShown: number[]
}

export interface PositionModeOptions {
  vesselsShown: number[]
}

export type MapState = {
  count: number
  viewState: MapViewState
  trackModeOptions: TrackModeOptions
  positionModeOptions: PositionModeOptions
  latestPositions: VesselPosition[]
  activePosition: VesselPosition | null
  trackedVesselIDs: number[]
  trackedVesselSegments: VesselExcursionSegments[]
  mode: "position" | "track"
  displayedZones: string[]
}

export type MapActions = {
  decrementCount: () => void
  incrementCount: () => void
  setViewState: (viewState: MapViewState) => void
  setZoom: (zoom: number) => void
  setLatestPositions: (latestPositions: VesselPosition[]) => void
  setActivePosition: (activePosition: VesselPosition | null) => void
  addTrackedVessel: (vesselID: number) => void
  removeTrackedVessel: (vesselID: number) => void
  clearLatestPositions: () => void
  cleartrackedVessels: () => void
  setMode: (mode: "position" | "track") => void

  setTrackModeOptions: (trackModeOptions: TrackModeOptions) => void

  setDisplayedZones: (zones: string[]) => void
  setPositionModeOptions: (positionModeOptions: PositionModeOptions) => void
}

export type MapStore = MapState & MapActions

export const defaultInitState: MapState = {
  count: 0,
  viewState: {
    longitude: 3.788086,
    latitude: 47.840291,
    zoom: 5,
    pitch: 20,
    bearing: 0,
  },
  latestPositions: [],
  activePosition: null,
  trackedVesselIDs: [],
  trackedVesselSegments: [],
  mode: "position",
  trackModeOptions: {
    startDate: undefined,
    endDate: undefined,
    vesselsIDsShown: [],
  },
  positionModeOptions: {
    vesselsShown: [],
  },
  displayedZones: [],
}

export const createMapStore = (initState: MapState = defaultInitState) => {
  return createStore<MapStore>()((set) => ({
    ...initState,
    setMode: (mode: "position" | "track") => {
      set((state) => ({
        ...state,
        mode,
      }))
    },
    decrementCount: () => set((state) => ({ count: state.count - 1 })),
    incrementCount: () => set((state) => ({ count: state.count + 1 })),
    setViewState: (viewState?: MapViewState) => {
      set((state) => ({
        ...state,
        viewState,
      }))
    },
    setZoom: (zoom: number) => {
      set((state) => ({
        ...state,
        viewState: { ...state.viewState, zoom },
      }))
    },
    setLatestPositions: (latestPositions: VesselPosition[]) => {
      set((state) => ({
        ...state,
        latestPositions,
      }))
    },
    setActivePosition: (activePosition: VesselPosition | null) => {
      set((state) => ({
        ...state,
        activePosition,
      }))
    },
    addTrackedVessel: (vesselId: number) => {
      set((state) => ({
        ...state,
        trackedVesselIDs: [...state.trackedVesselIDs, vesselId],
      }))
    },
    removeTrackedVessel: (vesselId: number) => {
      set((state) => ({
        ...state,
        trackedVesselIDs: state.trackedVesselIDs.filter(
          (id) => id !== vesselId
        ),
        trackedVesselSegments: state.trackedVesselSegments.filter(
          ({ vesselId }) => vesselId !== vesselId
        ),
      }))
    },
    clearLatestPositions: () => {
      set((state) => ({
        ...state,
        latestPositions: [],
      }))
    },
    cleartrackedVessels: () => {
      set((state) => ({
        ...state,
        trackedVesselIDs: [],
        trackedVesselSegments: [],
      }))
    },
    setDisplayedZones: (displayedZones: string[]) => {
      set((state) => ({
        ...state,
        displayedZones,
      }))
    },
    setTrackModeOptions: (trackModeOptions: TrackModeOptions) => {
      set((state) => ({
        ...state,
        trackModeOptions,
      }))
    },
    setPositionModeOptions: (positionModeOptions: PositionModeOptions) => {
      set((state) => ({
        ...state,
        positionModeOptions,
      }))
    },
  }))
}
