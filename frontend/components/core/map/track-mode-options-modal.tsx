import { EyeIcon } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { Switch } from "@/components/ui/switch"

import { FilterButton } from "./filter-button"
import { MapFilterModal } from "./map-filter-modal"

export function TrackModeOptionsModal() {
  const { showPositions, segmentMode, setShowPositions, setSegmentMode } =
    useTrackModeOptionsStore(
      useShallow((state) => ({
        showPositions: state.showPositions,
        segmentMode: state.segmentMode,
        setShowPositions: state.setShowPositions,
        setSegmentMode: state.setSegmentMode,
      }))
    )

  return (
    <MapFilterModal icon={EyeIcon} title="Options" description="Options">
      <div>
        <h6 className="mb-2 text-sm font-bold">Mode</h6>
        <div className="flex items-center gap-2">
          <FilterButton
            isActive={segmentMode === "speed"}
            onClick={() => setSegmentMode("speed")}
          >
            Speed
          </FilterButton>
          <FilterButton
            isActive={segmentMode === "vessel"}
            onClick={() => setSegmentMode("vessel")}
          >
            Vessel
          </FilterButton>
        </div>
      </div>
      <div>
        <h6 className="mb-2 text-sm font-bold">Display positions</h6>
        <div>
          <Switch
            className="h-4"
            checked={showPositions}
            onCheckedChange={setShowPositions}
          />
        </div>
      </div>
    </MapFilterModal>
  )
}
