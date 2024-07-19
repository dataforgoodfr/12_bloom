import Image from "next/image"
import Link from "next/link"
import { XIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import IconButton from "@/components/ui/icon-button"
import { useMapStore } from "@/components/providers/map-store-provider"
import { VesselPosition } from "@/types/vessel"
import { getVesselFirstExcursionSegments } from "@/services/backend-rest-client"

export interface PreviewCardTypes {
  vesselInfo: VesselPosition
}

const PreviewCard: React.FC<PreviewCardTypes> = ({ vesselInfo }) => {
  const {
    setActivePosition,
    addTrackedVessel,
    trackedVesselIDs,
    removeTrackedVessel,
  } = useMapStore((state) => state)
  const { vessel: { id: vesselId, mmsi, ship_name, imo, length }, timestamp } = vesselInfo
  const isVesselTracked = (vesselId: number) => {
    return trackedVesselIDs.includes(vesselId)
  }

  const handleDisplayTrail = async (vesselId: number) => {
    if (isVesselTracked(vesselId)) {
      removeTrackedVessel(vesselId);
      return;
    }
    const response = await getVesselFirstExcursionSegments(vesselId);
    addTrackedVessel(vesselId, response.data);
  }
  return (
    <div className="flex w-wrap flex-col rounded-t-lg bg-white shadow hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700 md:max-w-xl md:flex-row">
      <img
        className="h-[270px] w-2/5 overflow-hidden rounded-tl-lg object-cover"
        src="/img/scrombus.jpg"
        alt="default fishing vessel image"
      />

      <div className="flex grow flex-col px-4 py-2 leading-normal pt-4">
        <div className="flex w-full flex-row items-center justify-start gap-3">
          <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            {ship_name}
          </h5>
          <Image
            src="/flags/fr.svg"
            alt="country flag"
            width={24}
            height={18}
          />
        </div>
        <section id="vessel-details" className="mb-6">
          <p className="mb-3 text-sm text-gray-700 dark:text-gray-400">
            IMO {imo} / MMSI {mmsi}
          </p>
          <p className="mb-1 text-gray-700 dark:text-gray-400">
            <span className="font-bold">Vessel type:</span> Fishing Vessel
          </p>
          <p className="mb-1 text-gray-700 dark:text-gray-400">
            <span className="font-bold">Vessel length:</span> {length} meters
          </p>
          <p className="text-gray-700 dark:text-gray-400">
            <span className="font-bold">Last position:</span>
          </p>
          <p className="mb-1 text-gray-700 dark:text-gray-400">
            {timestamp}
          </p>
        </section>
        <section id="vessel-actions">
          <Button onClick={() => handleDisplayTrail(vesselId)}>
            {isVesselTracked(vesselId) ? "Hide" : "Display"} track
          </Button>
          {isVesselTracked(vesselId) && <Link href="#" className="ml-2">Show track details</Link>}
        </section>

        <div className="absolute right-0 top-0 pt-4 pr-3">
          <IconButton
            description="Close preview"
            onClick={() => setActivePosition(null)}
          >
            <XIcon className="size-5 text-black dark:text-white" />
          </IconButton>
        </div>
      </div>
    </div>
  )
}

export default PreviewCard
