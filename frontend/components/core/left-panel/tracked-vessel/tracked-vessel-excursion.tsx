import { useEffect, useMemo, useState } from "react"
import { CrosshairIcon, EyeIcon } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import {
  ExcursionMetrics,
  VesselExcursion,
  VesselExcursionTimeByZone,
} from "@/types/vessel"
import { ZoneCategory } from "@/types/zone"
import {
  convertDurationInSeconds,
  convertDurationToString,
} from "@/libs/dateUtils"
import { useTrackModeOptionsStore } from "@/libs/stores"
import SidebarExpander from "@/components/ui/custom/sidebar-expander"

import TrackedVesselMetric from "./tracked-vessel-metric"

export interface TrackedVesselExcursionProps {
  index: number
  excursion: VesselExcursion
  className?: string
}

function TimeByZoneDetail({
  timeByZone,
}: {
  timeByZone: VesselExcursionTimeByZone
}) {
  const durationInHours =
    Math.round(
      convertDurationInSeconds(timeByZone.vessel_visiting_time_by_zone) / 360
    ) / 10
  const durationFormatted = `${durationInHours}h`

  return (
    <div className="flex gap-2">
      <span className="text-md font-bold">{durationFormatted}</span>
      <div className="flex flex-col">
        <span className="text-sm font-bold">{timeByZone.zone.name}</span>
        <span className="text-sm text-color-4">
          {timeByZone.zone.sub_category}
        </span>
      </div>
    </div>
  )
}

export default function TrackedVesselExcursion({
  index,
  excursion,
  className,
}: TrackedVesselExcursionProps) {
  const prettifyDate = (date: string) => {
    return new Date(date).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    })
  }

  const [detailsOpened, setDetailsOpened] = useState(false)

  const {
    excursionsIDsHidden,
    toggleExcursionVisibility,
    setFocusedExcursionID,
    focusedExcursionID,
  } = useTrackModeOptionsStore(
    useShallow((state) => ({
      excursionsIDsHidden: state.excursionsIDsHidden,
      toggleExcursionVisibility: state.toggleExcursionVisibility,
      setFocusedExcursionID: state.setFocusedExcursionID,
      focusedExcursionID: state.focusedExcursionID,
    }))
  )

  const isHidden = useMemo(
    () => excursionsIDsHidden.includes(excursion.id),
    [excursionsIDsHidden, excursion.id]
  )
  const isFocused = useMemo(
    () => focusedExcursionID === excursion.id,
    [focusedExcursionID, excursion.id]
  )

  const onToggleVisibility = () => {
    toggleExcursionVisibility(excursion.id)
  }

  const onFocusExcursion = () => {
    if (isFocused) {
      setFocusedExcursionID(null)
    } else {
      setFocusedExcursionID(excursion.id)
    }
  }

  useEffect(() => {
    if (isFocused) {
      setDetailsOpened(true)
    }
  }, [isFocused])

  const title = useMemo(() => {
    let outputTitle = `Voyage ${index} | ${prettifyDate(excursion.departure_at)}`

    if (excursion.arrival_at) {
      outputTitle = `${outputTitle} - ${prettifyDate(excursion.arrival_at)}`
    } else {
      outputTitle = `${outputTitle} - ?`
    }

    return outputTitle
  }, [index, excursion])

  const metrics = useMemo(() => {
    return {
      totalTimeAtSea: convertDurationInSeconds(excursion.excursion_duration),
      mpa: convertDurationInSeconds(excursion.total_time_in_amp),
      frenchTerritorialWaters: convertDurationInSeconds(
        excursion.total_time_in_territorial_waters
      ),
      zonesWithNoFishingRights: convertDurationInSeconds(
        excursion.total_time_in_zones_with_no_fishing_rights
      ),
      aisDefault: convertDurationInSeconds(excursion.total_time_default_ais),
    } as ExcursionMetrics
  }, [excursion])

  return (
    <div className={`flex gap-1 ${className}`}>
      <SidebarExpander.Root
        className={`w-full justify-between ${isFocused ? "border-l-8 border-color-1" : ""}`}
        opened={detailsOpened}
        onToggle={setDetailsOpened}
      >
        <SidebarExpander.Header className="flex items-center justify-between">
          <h6 className={`text-sm font-bold`}>{title}</h6>
          <div className="flex gap-2">
            <button
              onClick={onToggleVisibility}
              className={`transition-colors hover:text-color-1/40 ${!isHidden ? "text-color-1" : ""}`}
            >
              <EyeIcon className="size-4" />
            </button>
            <button
              onClick={onFocusExcursion}
              className={`transition-colors hover:text-color-1/40 ${isFocused ? "text-color-1" : ""}`}
            >
              <CrosshairIcon className="size-4" />
            </button>
          </div>
        </SidebarExpander.Header>

        <SidebarExpander.Content>
          <div className="flex w-full flex-col">
            <TrackedVesselMetric
              title="Total time at sea"
              value={metrics.totalTimeAtSea}
              unit="time"
            />
            <TrackedVesselMetric
              title="MPA"
              value={metrics.mpa}
              baseValue={metrics.totalTimeAtSea}
              unit="time"
              className="flex flex-col gap-4"
            >
              {excursion.timeByMPAZone &&
                excursion.timeByMPAZone.length > 0 &&
                excursion.timeByMPAZone.map((timeByZone) => (
                  <TimeByZoneDetail
                    key={timeByZone.zone.id}
                    timeByZone={timeByZone}
                  />
                ))}
            </TrackedVesselMetric>
            <TrackedVesselMetric
              title="French Territorial Waters"
              value={metrics.frenchTerritorialWaters}
              baseValue={metrics.totalTimeAtSea}
              unit="time"
            />
            <TrackedVesselMetric
              title="Zones with no fishing rights"
              value={metrics.zonesWithNoFishingRights}
              baseValue={metrics.totalTimeAtSea}
              unit="time"
            />
            <TrackedVesselMetric
              title="AIS default"
              value={metrics.aisDefault}
              baseValue={metrics.totalTimeAtSea}
              unit="time"
            />
          </div>
        </SidebarExpander.Content>
      </SidebarExpander.Root>
    </div>
  )
}
