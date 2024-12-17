"use client"

import { Minus, Plus } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import { useMapStore } from "@/libs/stores/map-store"
import IconButton from "@/components/ui/icon-button"

import { TrackModeOptionsModal } from "./map/track-mode-options-modal"
import VesselFilterModal from "./map/vessel-filter-modal"
import ZoneFilterModal from "./map/zone-filter-modal"

interface MapControlsProps {
  zoneLoading: boolean
  vesselLoading: boolean
}

const MapControls = ({ zoneLoading, vesselLoading }: MapControlsProps) => {
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
    <div className="absolute right-0 top-0 m-8 flex flex-col items-end space-y-5">
      <IconButton description="Zoom In" onClick={() => handleZoomOut()}>
        <Plus className="size-5 text-black dark:text-white" />
      </IconButton>
      <IconButton description="Zoom Out" onClick={() => handleZoomIn()}>
        <Minus className="size-5 text-black dark:text-white" />
      </IconButton>
      <VesselFilterModal isLoading={vesselLoading} />
      <ZoneFilterModal
        activeZones={displayedZones}
        setActiveZones={setDisplayedZones}
        isLoading={zoneLoading}
      />
      <TrackModeOptionsModal />
    </div>
  )
}

export default MapControls
