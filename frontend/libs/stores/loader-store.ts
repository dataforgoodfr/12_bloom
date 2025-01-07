import { create } from "zustand"

interface ILoaderState {
  zonesLoading: boolean
  positionsLoading: boolean
  vesselsLoading: boolean
  excursionsLoading: boolean
  portsLoading: boolean
}

interface ILoaderActions {
  setZonesLoading: (isLoading: boolean) => void
  setPositionsLoading: (isLoading: boolean) => void
  setVesselsLoading: (isLoading: boolean) => void
  setExcursionsLoading: (isLoading: boolean) => void
  setPortsLoading: (isLoading: boolean) => void
}

export const useLoaderStore = create<ILoaderState & ILoaderActions>((set) => ({
  zonesLoading: false,
  positionsLoading: false,
  vesselsLoading: false,
  excursionsLoading: false,
  portsLoading: false,

  setZonesLoading: (isLoading) => set({ zonesLoading: isLoading }),
  setPositionsLoading: (isLoading) => set({ positionsLoading: isLoading }),
  setVesselsLoading: (isLoading) => set({ vesselsLoading: isLoading }),
  setExcursionsLoading: (isLoading) => set({ excursionsLoading: isLoading }),
  setPortsLoading: (isLoading) => set({ portsLoading: isLoading }),
}))
