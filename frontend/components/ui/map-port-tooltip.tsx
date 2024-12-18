import Link from "next/link"
import { getCountryNameFromIso3 } from "@/utils/vessel.utils"

import { Port } from "@/types/port"
import { ZoneWithGeometry } from "@/types/zone"
import Tooltip from "@/components/ui/custom/tooltip"

export interface MapPortTooltipProps {
  top: number
  left: number
  portInfo: Port
}

const MapPortTooltip = ({ top, left, portInfo }: MapPortTooltipProps) => {
  const { name, locode, country_iso3 } = portInfo

  return (
    <Tooltip top={top} left={left}>
      <div className="v max-w-[288px] overflow-hidden rounded-lg bg-slate-700 p-2 shadow-lg">
        <p className="mb-2 text-sm italic text-gray-200 dark:text-gray-400">
          Click to view on VesselFinder.com
        </p>
        <h5 className="mb-1 text-xl font-bold tracking-tight text-gray-100 dark:text-white">
          {name} - {getCountryNameFromIso3(country_iso3)}
        </h5>
        <p className="font-normal text-gray-200 dark:text-gray-400">{locode}</p>
      </div>
    </Tooltip>
  )
}

export default MapPortTooltip
