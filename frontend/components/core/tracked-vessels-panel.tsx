import { useEffect, useState } from "react"
import { Ship as ShipIcon, X } from "lucide-react"

import { Vessel } from "@/types/vessel"

import { useMapStore } from "../providers/map-store-provider"
import { useVesselsStore } from "../providers/vessels-store-provider"

type Props = {
  wideMode: boolean
  parentIsOpen: boolean
  openParent: () => void
}

export default function TrackedVesselsPanel({
  wideMode,
  parentIsOpen,
  openParent,
}: Props) {
  const { trackedVesselMMSIs, removeTrackedVesselMMSI } = useMapStore((state) => state);
  const { vessels: allVessels } = useVesselsStore((state) => state);
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
      trackedVesselMMSIs.includes(vessel.mmsi)
    )
    setTrackedVesselsDetails(vesselsDetails)
  }, [trackedVesselMMSIs])

  return (
    <>
      <button
        type="button"
        className="dark:highlight-white/5 flex items-center rounded-md bg-color-3 py-1.5 pl-1 pr-3 text-sm leading-6 text-slate-400 shadow-sm ring-0 ring-color-2 hover:bg-slate-700 hover:ring-slate-300"
        onClick={() => showOrHideTrackedVessels()}
      >
        <ShipIcon className="w-8 min-w-8" />
        {wideMode && (
          <span className="ml-2">{`Selected vessel (${trackedVesselMMSIs.length})`}</span>
        )}
      </button>

      {displayTrackedVessels &&
        parentIsOpen &&
        trackedVesselsDetails?.map((vessel: Vessel) => {
          return (
            <div key={vessel.id} className="mb-1 flex border-b-1 border-color-5 pb-1 text-xs text-slate-400">
              <div className="w-full pr-1">
                <div className="text-xxs text-white">{vessel.ship_name}</div>
                <div className="text-xxxs">
                  IMO {vessel.imo} / MMSI {vessel.mmsi} / Length {vessel.length}m
                </div>
              </div>
              <button
                className="block"
                onClick={() => removeTrackedVesselMMSI(vessel.mmsi)}
              >
                <X size={15} color="#2CE2B0" strokeWidth={2} />
              </button>
            </div>
          )
        })}
    </>
  )
}
