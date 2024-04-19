"use client"

import React from "react"
import { Layers, Minus, Plus, SlidersHorizontal } from "lucide-react"

import IconButton from "@/components/ui/icon-button"
import { useMapStore } from "@/components/providers/map-store-provider"

const MapControls = () => {
  const { viewState, setZoom } = useMapStore((state) => state)

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
      <IconButton description="Configure layers display settings">
        <Layers className="size-5 text-black dark:text-white" />
      </IconButton>
    </div>
  )
}

export default MapControls
