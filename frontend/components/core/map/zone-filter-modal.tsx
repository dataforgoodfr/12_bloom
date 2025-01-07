import { LayersIcon } from "lucide-react"

import { ZoneCategory } from "@/types/zone"

import { FilterButton } from "./filter-button"
import { MapFilterModal } from "./map-filter-modal"

interface ZoneFilterModalProps {
  activeZones: string[]
  setActiveZones: (zones: string[]) => void
  isLoading: boolean
  className?: string
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
  className,
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
    <MapFilterModal
      icon={LayersIcon}
      title="Zones"
      description="Configure layers display settings"
      loading={isLoading}
      disabled={isLoading}
      className={className}
      filterCount={activeZones.length}
    >
      <div className="flex flex-col gap-2">
        {zoneCategories.map((category) => (
          <FilterButton
            key={category}
            className="w-fit"
            isActive={activeZones.includes(category)}
            onClick={() => toggleFilter(category)}
          >
            {ZONE_LABELS.find((label) => label.category === category)?.label ||
              ""}
          </FilterButton>
        ))}
      </div>
    </MapFilterModal>
  )
}
