import { useMemo, useRef } from "react"
import Image from "next/image"
import { XIcon } from "lucide-react"

import { VesselPosition } from "@/types/vessel"
import { Button } from "@/components/ui/button"

export interface TooltipProps {
  top: number
  left: number
  width?: number
  height?: number
  isFrozen?: boolean
  onClose?: () => void
  children: React.ReactNode
}

const Tooltip = ({
  top,
  left,
  width,
  height,
  isFrozen = false,
  onClose,
  children,
}: TooltipProps) => {
  const tooltipRef = useRef<HTMLDivElement>(null)

  const topScreenSafe = useMemo(() => {
    const screenHeight = window.innerHeight
    const verticalOffset = 10
    const tooltipHeight = tooltipRef.current?.clientHeight ?? 0

    if (top + tooltipHeight + verticalOffset > screenHeight) {
      return top - tooltipHeight - verticalOffset
    }

    return top + verticalOffset
  }, [top, tooltipRef.current?.clientHeight])

  const leftScreenSafe = useMemo(() => {
    const screenWidth = window.innerWidth
    const horizontalOffset = 10
    const tooltipWidth = tooltipRef.current?.clientWidth ?? 0

    if (left + tooltipWidth + horizontalOffset > screenWidth) {
      return left - tooltipWidth - horizontalOffset
    }

    return left + horizontalOffset
  }, [left, tooltipRef.current?.clientWidth])

  return (
    <div
      className="absolute z-10"
      style={{
        top: topScreenSafe,
        left: leftScreenSafe,
        width: width,
        height: height,
      }}
      ref={tooltipRef}
    >
      <div className="flex size-full flex-col rounded-lg bg-white shadow">
        {isFrozen && (
          <div className="absolute right-2 top-2 z-20 text-background">
            <Button
              onClick={onClose}
              variant="ghost"
              size="icon"
              className="size-10 rounded-full p-1 hover:bg-background/20 hover:text-background"
            >
              <XIcon className="!size-6" />
            </Button>
          </div>
        )}
        {children}
      </div>
    </div>
  )
}

export default Tooltip
