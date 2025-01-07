import { create } from "zustand"

import { Vessel } from "@/types/vessel"

type VesselsState = {
  vessels: Vessel[]
  typeFilter: string[]
  classFilter: string[]
  countryFilter: string[]
}

type MapActions = {
  setVessels: (vessels: Vessel[]) => void
  setTypeFilter: (filter: string[]) => void
  setClassFilter: (filter: string[]) => void
  setCountryFilter: (filter: string[]) => void
}

type VesselsStore = VesselsState & MapActions

const defaultInitState: VesselsState = {
  vessels: [],
  typeFilter: [],
  classFilter: [],
  countryFilter: [],
}

export const useVesselsStore = create<VesselsStore>()((set, get) => ({
  ...defaultInitState,

  setVessels: (vessels: Vessel[]) => {
    set((state) => ({
      ...state,
      vessels,
    }))
  },
  setTypeFilter: (filter: string[]) =>
    set((state) => ({ ...state, typeFilter: filter })),

  setClassFilter: (filter: string[]) =>
    set((state) => ({ ...state, classFilter: filter })),

  setCountryFilter: (filter: string[]) =>
    set((state) => ({ ...state, countryFilter: filter })),
}))
