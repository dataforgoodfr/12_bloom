import { Vessel } from "@/types/vessel"
import { createStore } from "zustand/vanilla"

export type VesselsState = {
  count: number;
  vessels: Vessel[];
}

export type MapActions = {
  decrementCount: () => void
  incrementCount: () => void
  setVessels: (vessels: Vessel[]) => void
}

export type VesselsStore = VesselsState & MapActions

export const defaultInitState: VesselsState = {
  count: 0,
  vessels: [],
}

export const createVesselsStore = (initState: VesselsState = defaultInitState) => {
  return createStore<VesselsStore>()((set) => ({
    ...initState,
    decrementCount: () => set((state) => ({ count: state.count - 1 })),
    incrementCount: () => set((state) => ({ count: state.count + 1 })),
    setVessels: (vessels: Vessel[]) => {
      set((state) => ({
        ...state,
        vessels,
      }))
    }
  }))
}
