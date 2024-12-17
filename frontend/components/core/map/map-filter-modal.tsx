import { LucideIcon } from "lucide-react"

import { cn } from "@/libs/utils"
import Spinner from "@/components/ui/custom/spinner"
import IconButton from "@/components/ui/icon-button"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface MapFilterModalProps {
  icon: LucideIcon
  title: string
  description?: string
  children: React.ReactNode
  disabled?: boolean
  loading?: boolean
  className?: string
  filterCount?: number
}

export function MapFilterModal({
  icon: Icon,
  title,
  description,
  children,
  disabled = false,
  loading = false,
  className,
  filterCount = 0,
}: MapFilterModalProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <div className="relative">
          <IconButton disabled={disabled} description={description || ""}>
            {loading ? (
              <Spinner className="size-5 text-black dark:text-white" />
            ) : (
              <Icon className="size-5 text-black dark:text-white" />
            )}
          </IconButton>
          {filterCount > 0 && (
            <div className="absolute -top-1 right-[0.2rem] flex size-4 items-center justify-center rounded-full bg-primary text-xs font-medium text-black">
              {filterCount}
            </div>
          )}
        </div>
      </PopoverTrigger>
      <PopoverContent
        side="left"
        align="start"
        sideOffset={20}
        className={cn("w-72 bg-white", className)}
      >
        <div className="flex flex-col items-start gap-4 text-background">
          <h5 className="flex items-center gap-2">
            <Icon className="size-5 text-black dark:text-white" />
            <span className="font-bold uppercase text-background">{title}</span>
          </h5>
          {children}
        </div>
      </PopoverContent>
    </Popover>
  )
}
