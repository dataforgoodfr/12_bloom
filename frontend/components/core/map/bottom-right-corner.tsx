import { cn } from "@/libs/utils"

import MapLegend from "./map-legend"

function CoordonatesIndicator({
  coordinates,
  className,
}: {
  coordinates: string
  className: string
}) {
  return (
    <div
      className={cn(
        "w-fit bg-color-3 px-4 py-2 text-center text-xs text-color-4",
        className
      )}
    >
      {coordinates}
    </div>
  )
}

const BottomRightCorner = ({
  coordinates,
  className = "",
}: {
  coordinates: string
  className?: string
}) => {
  return (
    <div
      className={cn(
        "align-end absolute bottom-2 right-2 flex flex-col gap-2",
        className
      )}
    >
      <MapLegend className="rounded-lg shadow-lg" />
      <CoordonatesIndicator
        coordinates={coordinates}
        className="w-full justify-center rounded-lg shadow-lg"
      />
    </div>
  )
}

export default BottomRightCorner
