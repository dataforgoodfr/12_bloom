import { useEffect, useMemo, useState } from "react"
import { CrosshairIcon, EyeIcon } from "lucide-react"

import { VesselExcursion, ExcursionMetrics } from "@/types/vessel"
import SidebarExpander from "@/components/ui/custom/sidebar-expander"

import TrackedVesselMetric from "./tracked-vessel-metric"
import { useTrackModeOptionsStore } from "@/libs/stores"
import { useShallow } from "zustand/react/shallow"
import { convertDurationInSeconds } from "@/libs/dateUtils"

export interface TrackedVesselExcursionProps {
  index: number
  excursion: VesselExcursion
  className?: string
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

  const { excursionsIDsHidden, toggleExcursionVisibility, setFocusedExcursionID, focusedExcursionID } = useTrackModeOptionsStore(useShallow((state) => ({
    excursionsIDsHidden: state.excursionsIDsHidden,
    toggleExcursionVisibility: state.toggleExcursionVisibility,
    setFocusedExcursionID: state.setFocusedExcursionID,
    focusedExcursionID: state.focusedExcursionID,
  })))

  const isHidden = useMemo(() => excursionsIDsHidden.includes(excursion.id), [excursionsIDsHidden, excursion.id])

  const onToggleVisibility = () => {
    toggleExcursionVisibility(excursion.id)
  }

  const onFocusExcursion = () => {
    setFocusedExcursionID(excursion.id)
  }

  const isExcursionFocused = useMemo(() => {
    return focusedExcursionID === excursion.id
  }, [focusedExcursionID, excursion.id])

  useEffect(() => {
    if (isExcursionFocused) {
      setDetailsOpened(true)
    }
  }, [isExcursionFocused])

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
      totalTimeFishing: convertDurationInSeconds(excursion.excursion_duration),
      mpa: convertDurationInSeconds(excursion.total_time_in_amp),
      frenchTerritorialWaters: convertDurationInSeconds(excursion.total_time_in_territorial_waters),
      zonesWithNoFishingRights: convertDurationInSeconds(excursion.total_time_in_zones_with_no_fishing_rights),
      aisDefault: convertDurationInSeconds(excursion.total_time_default_ais),
    } as ExcursionMetrics
  }, [excursion])

  return (
    <div className={`flex gap-1 ${className}`}>
      <SidebarExpander.Root className="w-full justify-between" opened={detailsOpened} onToggle={setDetailsOpened}>
        <SidebarExpander.Header className="flex items-center justify-between">
          <h6 className={`text-sm font-bold ${isExcursionFocused ? 'text-color-1' : ''}`}>{title}</h6>
          <div className="flex gap-2">
            <button
              onClick={onToggleVisibility}
              className={`transition-colors hover:text-color-1 hover:text-color-1/40 ${!isHidden ? 'text-color-1' : ''}`}
            >
              <EyeIcon className="size-4" />
            </button>
            <button
              onClick={onFocusExcursion}
              className={`transition-colors hover:text-color-1 hover:text-color-1/40`}
            >
              <CrosshairIcon className="size-4" />
            </button>
          </div>
        </SidebarExpander.Header>

        <SidebarExpander.Content>
          <div className="flex w-full flex-col">
            <TrackedVesselMetric title="Total time fishing" value={metrics.totalTimeFishing} unit="time" />
            <TrackedVesselMetric title="MPA" value={metrics.mpa} baseValue={metrics.totalTimeFishing} unit="time" />
            <TrackedVesselMetric title="French Territorial Waters" value={metrics.frenchTerritorialWaters} baseValue={metrics.totalTimeFishing} unit="time" />
            <TrackedVesselMetric title="Zones with no fishing rights" value={metrics.zonesWithNoFishingRights} baseValue={metrics.totalTimeFishing} unit="time" />
            <TrackedVesselMetric title="AIS default" value={metrics.aisDefault} baseValue={metrics.totalTimeFishing} unit="time" />
          </div>
        </SidebarExpander.Content>
      </SidebarExpander.Root>
    </div>
  )
}
