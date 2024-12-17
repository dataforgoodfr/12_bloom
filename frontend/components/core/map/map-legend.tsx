import { useShallow } from "zustand/react/shallow"

import { useMapStore, useTrackModeOptionsStore } from "@/libs/stores"
import { cn } from "@/libs/utils"

export interface MapLegendProps {
  className?: string
}

export default function MapLegend({ className }: MapLegendProps) {
  const { showPositions, segmentMode } = useTrackModeOptionsStore(
    useShallow((state) => ({
      showPositions: state.showPositions,
      segmentMode: state.segmentMode,
    }))
  )

  const { mode: mapMode } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
    }))
  )

  if (mapMode !== "track") return null

  return (
    <div className={cn("flex flex-col gap-4 bg-color-3 p-4", className)}>
      <div className="flex flex-col gap-2">
        <h6 className="text-sm font-bold text-white">Segment</h6>
        <ul className="flex flex-col gap-2 pl-4">
          <li className="flex items-center gap-3">
            <span className="h-px w-6 border-b-2 border-white"></span>
            <span className="text-xs text-white">At sea</span>
          </li>
          <li className="flex items-center gap-3">
            <span className="h-px w-6 border-b-2 border-dashed border-white"></span>
            <span className="text-xs text-white">Default AIS</span>
          </li>
          <li className="flex items-center gap-3">
            <span className="h-px w-6 border-b-4 border-white"></span>
            <span className="text-xs text-white">Fishing</span>
          </li>
        </ul>
      </div>
      {segmentMode === "speed" && (
        <div className="flex flex-col gap-2">
          <h6 className="text-sm font-bold text-white">Speed (knots)</h6>
          <div className="flex h-16 items-center gap-2 pl-4">
            <div className="h-full w-2 rounded-full bg-gradient-to-b from-yellow-500 to-red-500"></div>
            <div className="flex h-full flex-col justify-between gap-1">
              <span className="text-xs text-white">0</span>
              <span className="text-xs text-white">10</span>
              <span className="text-xs text-white">20</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
