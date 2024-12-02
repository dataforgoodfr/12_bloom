import { useMemo, useState } from "react"
import { motion, useAnimationControls } from "framer-motion"
import { ChevronUpIcon, CrosshairIcon, EyeIcon } from "lucide-react"

import { VesselExcursion } from "@/types/vessel"
import Toggle from "@/components/ui/custom/toggle"

import TrackedVesselMetric from "./tracked-vessel-metric"

export interface TrackedVesselExcursionProps {
  index: number
  excursion: VesselExcursion
  onView: () => void
  onFocus: () => void
  className?: string
}

export default function TrackedVesselExcursion({
  index,
  excursion,
  onView,
  onFocus,
  className,
}: TrackedVesselExcursionProps) {
  const prettifyDate = (date: string) => {
    return new Date(date).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    })
  }

  const title = useMemo(() => {
    let outputTitle = `Voyage ${index} | ${prettifyDate(excursion.departure_at)}`

    if (excursion.arrival_at) {
      outputTitle = `${outputTitle} - ${prettifyDate(excursion.arrival_at)}`
    } else {
      outputTitle = `${outputTitle} - ?`
    }

    return outputTitle
  }, [excursion])

  return (
    <div className="flex gap-1">
      <Toggle.Root className="w-full justify-between">
        <Toggle.Header className="flex items-center justify-between">
          <h6 className="text-sm font-bold">{title}</h6>
          <div className="flex gap-2">
            <button
              onClick={onView}
              className="transition-colors hover:text-color-1"
            >
              <EyeIcon className="size-4" />
            </button>
            <button
              onClick={onFocus}
              className="transition-colors hover:text-color-1"
            >
              <CrosshairIcon className="size-4" />
            </button>
          </div>
        </Toggle.Header>

        <Toggle.Content>
          <div className="flex w-full flex-col">
            <TrackedVesselMetric title="Total time fishing" value={1234} unit="time" />
            <TrackedVesselMetric title="MPA" value={123438} baseValue={2345} unit="time" >
              <p>Details</p>
            </TrackedVesselMetric>
            <TrackedVesselMetric title="French Territorial Waters" value={123438} baseValue={123439} unit="time" />
            <TrackedVesselMetric title="Zones with no fishing rights" value={1} baseValue={100} unit="time" />
            <TrackedVesselMetric title="AIS default" value={37.2} baseValue={100} unit="time" />
          </div>
        </Toggle.Content>
      </Toggle.Root>
    </div>
  )
}
