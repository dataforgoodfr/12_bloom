import { useState } from "react"
import { EyeIcon } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { cn } from "@/libs/utils"
import { Button } from "@/components/ui/button"
import IconButton from "@/components/ui/icon-button"
import { Switch } from "@/components/ui/switch"

function RadioButton({
  children,
  checked,
  onClick,
  className,
}: {
  children: React.ReactNode
  checked: boolean
  onClick: () => void
  className?: string
}) {
  return (
    <Button
      variant="outline"
      className={cn(
        "h-8",
        checked
          ? "bg-primary text-white hover:bg-primary/90"
          : "bg-gray-100 text-black hover:bg-gray-200 hover:text-black",
        className
      )}
      onClick={onClick}
    >
      {children}
    </Button>
  )
}

export function TrackModeOptionsModal() {
  const [opened, setOpened] = useState(false)

  const handleClick = () => {
    setOpened(!opened)
  }

  const { showPositions, segmentMode, setShowPositions, setSegmentMode } =
    useTrackModeOptionsStore(
      useShallow((state) => ({
        showPositions: state.showPositions,
        segmentMode: state.segmentMode,
        setShowPositions: state.setShowPositions,
        setSegmentMode: state.setSegmentMode,
      }))
    )

  return (
    <div className="flex items-start gap-4 text-background">
      {opened && (
        <div className="flex w-96 flex-col gap-4 rounded-lg bg-white p-4">
          <h5 className="flex items-center gap-2">
            <EyeIcon className="size-5 text-black dark:text-white" />
            <span className="font-bold uppercase">Options</span>
          </h5>
          <div>
            <h6 className="mb-2 text-sm font-bold">Mode</h6>
            <div className="flex items-center gap-2">
              <RadioButton
                checked={segmentMode === "speed"}
                onClick={() => setSegmentMode("speed")}
              >
                Speed
              </RadioButton>
              <RadioButton
                checked={segmentMode === "vessel"}
                onClick={() => setSegmentMode("vessel")}
              >
                Vessel
              </RadioButton>
            </div>
          </div>
          <div>
            <h6 className="mb-2 text-sm font-bold">Display positions</h6>
            <div>
              <Switch
                className="h-4"
                checked={showPositions}
                onCheckedChange={setShowPositions}
              />
            </div>
          </div>
        </div>
      )}
      <IconButton description="Set filters" onClick={handleClick}>
        <EyeIcon className="size-5 text-black dark:text-white" />
      </IconButton>
    </div>
  )
}
