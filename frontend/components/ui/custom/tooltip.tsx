import { useEffect, useMemo, useRef, useState } from "react"
import { XIcon } from "lucide-react"

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
  const [isVisible, setIsVisible] = useState(false)

  const topScreenSafe = useMemo(() => {
    const screenHeight = window.innerHeight
    const verticalOffset = 10
    const tooltipHeight = tooltipRef.current?.clientHeight ?? 0

    let topScreenSafe = top + verticalOffset

    if (topScreenSafe + tooltipHeight > screenHeight) {
      topScreenSafe = top - tooltipHeight - verticalOffset
    }

    return Math.max(topScreenSafe, 0)
  }, [top, tooltipRef.current?.clientHeight])

  const leftScreenSafe = useMemo(() => {
    const screenWidth = window.innerWidth
    const horizontalOffset = 10
    const tooltipWidth = tooltipRef.current?.clientWidth ?? 0

    let leftScreenSafe = left + horizontalOffset

    if (leftScreenSafe + tooltipWidth > screenWidth) {
      leftScreenSafe = left - tooltipWidth - horizontalOffset
    }

    return Math.max(leftScreenSafe, 0)
  }, [left, tooltipRef.current?.clientWidth])

  useEffect(() => {
    if (!isVisible && tooltipRef.current?.clientWidth) {
      setIsVisible(true)
    }
  }, [tooltipRef.current?.clientWidth])

  return (
    <div
      className="absolute z-10"
      style={{
        top: topScreenSafe,
        left: leftScreenSafe,
        width: width,
        height: height,
        visibility: isVisible ? "visible" : "hidden",
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
