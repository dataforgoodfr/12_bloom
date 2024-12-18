import { SegmentVesselPosition } from "@/types/vessel"
import Tooltip from "@/components/ui/custom/tooltip"

export interface SegmentPositionTooltipProps {
  top: number
  left: number
  segmentPositionInfo: SegmentVesselPosition
}

const SegmentPositionTooltip = ({
  top,
  left,
  segmentPositionInfo,
}: SegmentPositionTooltipProps) => {
  const { timestamp, position, heading, speed } = segmentPositionInfo

  const formattedTimestamp = new Date(timestamp)
    .toLocaleString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "UTC",
      timeZoneName: "short",
    })
    .replace(",", " -")

  const speedRounded = speed ? `${speed.toFixed(1)}` : null

  return (
    <Tooltip top={top} left={left}>
      <div className="max-w-[288px] rounded-lg shadow-lg">
        <div className="bg-slate-700 p-3">
          <p className="text-sm text-white">{formattedTimestamp}</p>
          {speed && (
            <p className="font-normal text-gray-200 dark:text-gray-400">
              {speedRounded} knots
            </p>
          )}
        </div>
      </div>
    </Tooltip>
  )
}

export default SegmentPositionTooltip
