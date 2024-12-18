import { create } from "zustand"

import { Port } from "@/types/port"

type PortsState = {
  ports: Port[]
}

type MapActions = {
  setPorts: (ports: Port[]) => void
}

type PortsStore = PortsState & MapActions

const defaultInitState: PortsState = {
  ports: [],
}

export const usePortsStore = create<PortsStore>()((set, get) => ({
  ...defaultInitState,

  setPorts: (ports: Port[]) => {
    set((state) => ({
      ...state,
      ports,
    }))
  },
}))
