"use client"

import { createContext, useContext, useRef, type ReactNode } from "react"
import { useStore, type StoreApi } from "zustand"
import { VesselsState, createVesselsStore, type VesselsStore } from "@/lib/stores/vessels-store"

export const VesselsStoreContext = createContext<StoreApi<VesselsStore> | null>(null)

export interface VesselsStoreProviderProps {
  children: ReactNode
}

export const VesselsStoreProvider = ({ children }: VesselsStoreProviderProps) => {
  const storeRef = useRef<StoreApi<VesselsStore>>()
  if (!storeRef.current) {
    storeRef.current = createVesselsStore()
  }

  return (
    <VesselsStoreContext.Provider value={storeRef.current}>
      {children}
    </VesselsStoreContext.Provider>
  )
}

export const useVesselsStore = <T,>(selector: (store: VesselsStore) => T): T => {
  const context = useContext(VesselsStoreContext)

  if (!context) {
    throw new Error(`useVesselsStore must be use within VesselsStoreProvider`)
  }

  return useStore(context, selector)
}
