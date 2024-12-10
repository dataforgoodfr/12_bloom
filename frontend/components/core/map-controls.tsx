"use client"

import React from "react"
import { Layers, Minus, Plus, SlidersHorizontal } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import { useMapStore } from "@/libs/stores/map-store"
import IconButton from "@/components/ui/icon-button"

import ZoneFilterModal from "./map/zone-filter-modal"

interface MapControlsProps {
  zoneLoading: boolean
}

const MapControls = ({ zoneLoading }: MapControlsProps) => {
  const { viewState, setZoom, displayedZones, setDisplayedZones } = useMapStore(
    useShallow((state) => ({
      viewState: state.viewState,
      setZoom: state.setZoom,
      displayedZones: state.displayedZones,
      setDisplayedZones: state.setDisplayedZones,
    }))
  )

  const handleZoomIn = () => {
    setZoom(viewState.zoom - 1)
  }
  const handleZoomOut = () => {
    setZoom(viewState.zoom + 1)
  }
  return (
    <div className="absolute right-0 top-0 m-8 flex flex-col items-center space-y-5">
      <IconButton description="Zoom In" onClick={() => handleZoomOut()}>
        <Plus className="size-5 text-black dark:text-white" />
      </IconButton>
      <IconButton description="Zoom Out" onClick={() => handleZoomIn()}>
        <Minus className="size-5 text-black dark:text-white" />
      </IconButton>
      <IconButton description="Set filters">
        <SlidersHorizontal className="size-5 text-black dark:text-white" />
      </IconButton>
      <ZoneFilterModal
        activeZones={displayedZones}
        setActiveZones={setDisplayedZones}
        isLoading={zoneLoading}
      />
    </div>
  )
}

export default MapControls
