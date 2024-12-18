import { ZoneWithGeometry } from "@/types/zone"
import Tooltip from "@/components/ui/custom/tooltip"

export interface MapZoneTooltipProps {
  top: number
  left: number
  zoneInfo: ZoneWithGeometry
}

const MapZoneTooltip = ({ top, left, zoneInfo }: MapZoneTooltipProps) => {
  const { name, category, sub_category } = zoneInfo

  return (
    <Tooltip top={top} left={left}>
      <div className="max-w-[288px] rounded-lg shadow-lg">
        <div className="bg-slate-700 p-5">
          <h5 className="mb-1 text-xl font-bold tracking-tight text-gray-100 dark:text-white">
            {name}
          </h5>
          <p className="font-normal text-gray-200 dark:text-gray-400">
            {category} / {sub_category}
          </p>
        </div>
      </div>
    </Tooltip>
  )
}

export default MapZoneTooltip
