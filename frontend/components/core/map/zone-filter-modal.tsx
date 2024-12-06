import Image from "next/image"

import { ZoneCategory } from "@/types/zone"
import Spinner from "@/components/ui/custom/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import IconButton from "@/components/ui/icon-button"

import { FilterButton } from "./filter-button"

interface ZoneFilterModalProps {
  activeZones: string[]
  setActiveZones: (zones: string[]) => void
  isLoading: boolean
}

const ZONE_LABELS = [
  {
    category: ZoneCategory.AMP,
    label: "MPA",
  },
  {
    category: ZoneCategory.FISHING_COASTAL_WATERS,
    label: "Fishing coastal waters",
  },
  {
    category: ZoneCategory.TERRITORIAL_SEAS,
    label: "Territorial waters",
  },
]

export default function ZoneFilterModal({
  activeZones,
  setActiveZones,
  isLoading,
}: ZoneFilterModalProps) {
  const zoneCategories = Object.values(ZoneCategory)

  const toggleFilter = (filter: string) => {
    setActiveZones(
      activeZones.includes(filter)
        ? activeZones.filter((f) => f !== filter)
        : [...activeZones, filter]
    )
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <IconButton
          disabled={isLoading}
          description="Configure layers display settings"
        >
          {isLoading ? (
            <Spinner />
          ) : (
            <Image
              src="/icons/card-file.svg"
              alt="Layers"
              width={26}
              height={26}
            />
          )}
        </IconButton>
      </DialogTrigger>
      <DialogContent className="flex w-64 flex-col gap-6 bg-white">
        <DialogHeader className="flex flex-row items-center justify-between space-y-0">
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Image
              src="/icons/card-file.svg"
              alt="Layers"
              width={26}
              height={26}
            />
            Zones
          </DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-2.5">
          {zoneCategories.map((category) => (
            <FilterButton
              key={category}
              value={category}
              label={
                ZONE_LABELS.find((label) => label.category === category)
                  ?.label || ""
              }
              isActive={activeZones.includes(category)}
              onToggle={toggleFilter}
            />
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
