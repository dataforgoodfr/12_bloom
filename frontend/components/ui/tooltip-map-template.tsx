import { VesselPosition } from "@/types/vessel"
import Image from "next/image"

export interface MapTooltipTypes {
  vesselInfo: VesselPosition
  orientation?: "landscape" | "portrait"
}

const MapTooltip = ({
  vesselInfo,
  orientation = "portrait",
}: MapTooltipTypes) => {
  const { vessel: { mmsi, ship_name, imo, length }, timestamp } = vesselInfo

  return (
    <>
      {orientation === "portrait" && (
        <div className="max-w-[288px] rounded-lg border border-gray-200 bg-white shadow dark:border-gray-700 dark:bg-gray-800">
          <Image
            className="rounded-t-lg"
            src="/img/scrombus.jpg"
            alt="default fishing vessel image"
            width={288}
            height={162}
          />
          <Image
            className="absolute bottom-[182px] left-5 z-20"
            src="/flags/fr.svg"
            alt="country flag"
            width={36}
            height={24}
          />
          <div className="bg-slate-700 p-5">
            <h5 className="mb-1 text-xl font-bold tracking-tight text-gray-100 dark:text-white">
              {ship_name}
            </h5>
            <p className="mb-3 font-normal text-gray-200 dark:text-gray-400">
              IMO {imo} / MMSI {mmsi}
            </p>
            <p className="mb-1 font-normal text-gray-200 dark:text-gray-400">
              <span className="font-bold">Vessel type</span> Fishing Vessel
            </p>
            <p className="mb-1 font-normal text-gray-200 dark:text-gray-400">
              <span className="font-bold">Vessel size:</span> {length} meters
            </p>
            <p className="font-normal text-gray-200 dark:text-gray-400">
              <span className="font-bold">Last position timestamp:</span>
            </p>
            <p className="mb-1 font-normal text-gray-200 dark:text-gray-400">
              {timestamp}
            </p>
          </div>
        </div>
      )}
    </>
  )
}

export default MapTooltip
