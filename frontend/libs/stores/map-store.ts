import { MapViewState } from "@deck.gl/core"
import { create } from "zustand"

import { VesselExcursion, VesselPosition } from "@/types/vessel"

interface IMapState {
  viewState: MapViewState
  latestPositions: VesselPosition[]
  mode: "position" | "track"
  displayedZones: string[]
  activePosition: VesselPosition | null
  leftPanelOpened: boolean
}

interface IMapActions {
  setViewState: (viewState: MapViewState) => void
  setZoom: (zoom: number) => void
  setLatestPositions: (latestPositions: VesselPosition[]) => void
  clearLatestPositions: () => void
  setMode: (mode: "position" | "track") => void
  setDisplayedZones: (zones: string[]) => void
  setActivePosition: (activePosition: VesselPosition | null) => void
  setLeftPanelOpened: (leftPanelOpened: boolean) => void
}

type IMapStore = IMapState & IMapActions

const defaultInitState: IMapState = {
  viewState: {
    longitude: 3.788086,
    latitude: 47.840291,
    zoom: 5,
    pitch: 0,
    bearing: 0,
  },
  latestPositions: [],
  mode: "position",
  displayedZones: [],
  activePosition: null,
  leftPanelOpened: false,
}

export const useMapStore = create<IMapStore>()((set) => ({
  ...defaultInitState,

  setMode: (mode: "position" | "track") => {
    set((state) => ({
      ...state,
      mode,
    }))
  },
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
  clearLatestPositions: () => {
    set((state) => ({
      ...state,
      latestPositions: [],
    }))
  },
  setDisplayedZones: (displayedZones: string[]) => {
    set((state) => ({
      ...state,
      displayedZones,
    }))
  },
  setLeftPanelOpened: (leftPanelOpened: boolean) => {
    set((state) => ({
      ...state,
      leftPanelOpened,
    }))
  },
}))
