import { create } from "zustand"

import { Vessel } from "@/types/vessel"

type VesselsState = {
  count: number
  vessels: Vessel[]
}

type MapActions = {
  decrementCount: () => void
  incrementCount: () => void
  setVessels: (vessels: Vessel[]) => void
}

type VesselsStore = VesselsState & MapActions

const defaultInitState: VesselsState = {
  count: 0,
  vessels: [],
}

export const useVesselsStore = create<VesselsStore>()((set) => ({
  ...defaultInitState,

  decrementCount: () => set((state) => ({ count: state.count - 1 })),
  incrementCount: () => set((state) => ({ count: state.count + 1 })),
  setVessels: (vessels: Vessel[]) => {
    set((state) => ({
      ...state,
      vessels,
    }))
  },
}))
