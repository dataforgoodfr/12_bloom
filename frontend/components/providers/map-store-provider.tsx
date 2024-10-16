"use client"

import { createContext, useContext, useRef, type ReactNode } from "react"
import { useStore, type StoreApi } from "zustand"

import { createMapStore, type MapStore } from "@/libs/stores/map-store"

export const MapStoreContext = createContext<StoreApi<MapStore> | null>(null)

export interface MapStoreProviderProps {
  children: ReactNode
}

export const MapStoreProvider = ({ children }: MapStoreProviderProps) => {
  const storeRef = useRef<StoreApi<MapStore>>()
  if (!storeRef.current) {
    storeRef.current = createMapStore()
  }

  return (
    <MapStoreContext.Provider value={storeRef.current}>
      {children}
    </MapStoreContext.Provider>
  )
}

export const useMapStore = <T,>(selector: (store: MapStore) => T): T => {
  const mapStoreContext = useContext(MapStoreContext)

  if (!mapStoreContext) {
    throw new Error(`useMapStore must be use within MapStoreProvider`)
  }

  return useStore(mapStoreContext, selector)
}
