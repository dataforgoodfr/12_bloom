
import { ZoneWithGeometry } from "@/types/zone"

export interface ZoneMapTooltipProps {
  zoneInfo: ZoneWithGeometry
}

const ZoneMapTooltip = ({ zoneInfo }: ZoneMapTooltipProps) => {
  const { name, category, sub_category } = zoneInfo

  return (
    <>
      <div className="max-w-[288px] rounded-lg border border-gray-200 bg-white shadow dark:border-gray-700 dark:bg-gray-800">
        <div className="bg-slate-700 p-5">
          <h5 className="mb-1 text-xl font-bold tracking-tight text-gray-100 dark:text-white">
            {name}
          </h5>
          <p className="mb-3 font-normal text-gray-200 dark:text-gray-400">
            {category} / {sub_category}
          </p>
        </div>
      </div>
    </>
  )
}

export default ZoneMapTooltip
