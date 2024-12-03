import { useMemo } from "react"
import { EyeIcon, XIcon } from "lucide-react"

import { Vessel } from "@/types/vessel"
import Toggle from "@/components/ui/custom/toggle"

import TrackedVesselDetails from "./tracked-vessel-details"

const shipColorsBackground = [
  "bg-vessel-color-1",
  "bg-vessel-color-2",
  "bg-vessel-color-3",
  "bg-vessel-color-4",
  "bg-vessel-color-5",
  "bg-vessel-color-6",
  "bg-vessel-color-7",
  "bg-vessel-color-8",
  "bg-vessel-color-9",
  "bg-vessel-color-10",
  "bg-vessel-color-11",
  "bg-vessel-color-12",
]

export interface TrackedVesselItemProps {
  showDetails: boolean
  colorIndex: number
  vessel: Vessel
  onRemove: (vesselID: number) => void
  onView: () => void
  className?: string
}

export default function TrackedVesselItem({
  showDetails,
  vessel,
  colorIndex = 0,
  onRemove,
  onView,
  className,
}: TrackedVesselItemProps) {
  const vesselBgColorClass = useMemo(() => {
    return shipColorsBackground[colorIndex]
  }, [colorIndex])

  return (
    <div className="flex gap-1">
      <div className={`flex w-full flex-col gap-2 py-2 ${className}`}>
        <Toggle.Root disabled={!showDetails}>
          <Toggle.Header className="flex items-center justify-between">
            <div className="flex w-full flex-col gap-1">
              <div className="flex items-center gap-2">
                <div
                  className={`rounded-full ${vesselBgColorClass} size-4`}
                ></div>
                <h6 className="text-sm font-bold">{vessel.ship_name}</h6>
              </div>
              <div>
                <p className="text-sm text-color-4">
                  IMO {vessel.imo} / MMSI {vessel.mmsi} / {vessel.length}m
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => onRemove(vessel.id)}
                className="transition-colors hover:text-color-1"
              >
                <XIcon className="size-4" />
              </button>
              <button
                onClick={onView}
                className="transition-colors hover:text-color-1"
              >
                <EyeIcon className="size-4" />
              </button>
            </div>
          </Toggle.Header>
          <Toggle.Content>
            <div className="flex w-full  flex-col">
              <TrackedVesselDetails
                vessel={vessel}
                onExcursionView={() => {}}
                onExcursionFocus={() => {}}
              />
            </div>
          </Toggle.Content>
        </Toggle.Root>
      </div>
    </div>
  )
}
