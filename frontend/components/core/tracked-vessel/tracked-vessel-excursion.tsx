import { useMemo } from "react"
import { CrosshairIcon, EyeIcon } from "lucide-react"

import { VesselExcursion } from "@/types/vessel"
import SidebarExpander from "@/components/ui/custom/sidebar-expander"

import TrackedVesselMetric from "./tracked-vessel-metric"
import { useTrackModeOptionsStore } from "@/libs/stores"
import { useShallow } from "zustand/react/shallow"

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

  const { excursionsIDsHidden, toggleExcursionVisibility, setFocusedExcursionID } = useTrackModeOptionsStore(useShallow((state) => ({
    excursionsIDsHidden: state.excursionsIDsHidden,
    toggleExcursionVisibility: state.toggleExcursionVisibility,
    setFocusedExcursionID: state.setFocusedExcursionID,
  })))

  const isHidden = useMemo(() => excursionsIDsHidden.includes(excursion.id), [excursionsIDsHidden, excursion.id])

  const onToggleVisibility = () => {
    toggleExcursionVisibility(excursion.id)
  }

  const onFocusExcursion = () => {
    setFocusedExcursionID(excursion.id)
  }

  const title = useMemo(() => {
    let outputTitle = `Voyage ${index} | ${prettifyDate(excursion.departure_at)}`

    if (excursion.arrival_at) {
      outputTitle = `${outputTitle} - ${prettifyDate(excursion.arrival_at)}`
    } else {
      outputTitle = `${outputTitle} - ?`
    }

    return outputTitle
  }, [index, excursion])

  return (
    <div className={`flex gap-1 ${className}`}>
      <SidebarExpander.Root className="w-full justify-between">
        <SidebarExpander.Header className="flex items-center justify-between">
          <h6 className="text-sm font-bold">{title}</h6>
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
            <TrackedVesselMetric title="Total time fishing" value={1234} unit="time" />
            <TrackedVesselMetric title="MPA" value={123438} baseValue={2345} unit="time" >
              <p>Details</p>
            </TrackedVesselMetric>
            <TrackedVesselMetric title="French Territorial Waters" value={123438} baseValue={123439} unit="time" />
            <TrackedVesselMetric title="Zones with no fishing rights" value={1} baseValue={100} unit="time" />
            <TrackedVesselMetric title="AIS default" value={37.2} baseValue={100} unit="time" />
          </div>
        </SidebarExpander.Content>
      </SidebarExpander.Root>
    </div>
  )
}
