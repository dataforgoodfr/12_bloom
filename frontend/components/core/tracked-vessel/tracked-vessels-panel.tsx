"use client"

import { useEffect, useState } from "react"
import { ChevronRight, PenIcon, Ship as ShipIcon } from "lucide-react"

import { Vessel } from "@/types/vessel"
import { Button } from "@/components/ui/button"

import { useMapStore } from "@/components/providers/map-store-provider"
import { useVesselsStore } from "@/components/providers/vessels-store-provider"
import TrackedVesselItem from "./tracked-vessel-item"

type Props = {
  wideMode: boolean
  parentIsOpen: boolean
  openParent: () => void
}

function NoVesselsPlaceholder() {
  return (
    <p className="flex items-center rounded-md py-1.5 pl-1 pr-3 text-sm leading-6 text-slate-400">
      <span>There is no vessels selected</span>
    </p>
  )
}

function VesselsActions({
  onCreateFleet = () => {},
  disabledCreateFleet = false,
  onViewTracks = () => {},
  disabledViewTracks = false,
}: {
  onCreateFleet?: () => void
  disabledCreateFleet?: boolean
  onViewTracks?: () => void
  disabledViewTracks?: boolean
}) {
  return (
    <div className="flex justify-center gap-1">
      <Button
        variant="outline"
        onClick={onCreateFleet}
        disabled={disabledCreateFleet}
        className="border border-color-1 bg-inherit text-color-1"
        color="primary"
      >
        <PenIcon className="size-4" />
        Create fleet
      </Button>
      <Button
        onClick={onViewTracks}
        disabled={disabledViewTracks}
        color="primary"
      >
        View tracks
        <ChevronRight className="size-4" />
      </Button>
    </div>
  )
}

export default function TrackedVesselsPanel({
  wideMode,
  parentIsOpen,
  openParent,
}: Props) {
  const { trackedVesselIDs, removeTrackedVessel } = useMapStore(
    (state) => state
  )
  const { vessels: allVessels } = useVesselsStore((state) => state)
  const [displayTrackedVessels, setDisplayTrackedVessels] = useState(false)
  const [trackedVesselsDetails, setTrackedVesselsDetails] = useState<Vessel[]>()

  const showOrHideTrackedVessels = () => {
    if (!parentIsOpen) {
      openParent()
    }
    setDisplayTrackedVessels(!displayTrackedVessels)
  }

  useEffect(() => {
    const vesselsDetails = allVessels.filter((vessel) =>
      trackedVesselIDs.includes(vessel.id)
    )
    setTrackedVesselsDetails(vesselsDetails)
  }, [allVessels, trackedVesselIDs])

  const onRemoveVesselTracked = (vesselID: number) => {
    removeTrackedVessel(vesselID)
  }

  const WideModeTab = () => {
    return (
      <>
        {trackedVesselIDs.length === 0 && <NoVesselsPlaceholder />}

        {trackedVesselsDetails?.map((vessel: Vessel, index) => {
          return (
            <TrackedVesselItem
              key={vessel.id}
              vessel={vessel}
              colorIndex={index}
              onRemove={onRemoveVesselTracked}
              onView={() => {}}
              className={`${
                index < allVessels.slice(10, 20).length - 1
                  ? "border-b border-color-3"
                  : ""
              }`}
            />
          )
        })}

        <VesselsActions
          disabledCreateFleet={true}
          onViewTracks={() => {
            console.log("View tracks")
          }}
          disabledViewTracks={true}
        />
      </>
    )
  }

  return (
    <>
      <div>
        <h5
          className="flex gap-1 text-sm font-bold uppercase leading-6"
          onClick={() => showOrHideTrackedVessels()}
        >
          <ShipIcon className="w-8 min-w-8" />
          {wideMode && (
            <span>{`Selected vessel (${trackedVesselIDs.length})`}</span>
          )}
        </h5>
      </div>

      {wideMode && <WideModeTab />}
    </>
  )
}
