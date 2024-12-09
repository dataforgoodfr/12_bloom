"use client"

import TrackedVesselMetric from "./tracked-vessel-metric"
import { Vessel, VesselExcursion } from "@/types/vessel"
import TrackedVesselExcursion from "./tracked-vessel-excursion"
import { useShallow } from "zustand/react/shallow"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { useLoaderStore } from "@/libs/stores/loader-store"

import { useMemo } from "react"
import Spinner from "@/components/ui/custom/spinner"


export interface TrackedVesselDetailsProps {
  vessel: Vessel
  className?: string
}

export default function TrackedVesselDetails({
  vessel,
  className,
}: TrackedVesselDetailsProps) {
  const { excursions } = useTrackModeOptionsStore(useShallow((state) => ({
    excursions: state.excursions,
  })))

  const { excursionsLoading } = useLoaderStore(useShallow((state) => ({
    excursionsLoading: state.excursionsLoading,
  })))

  const vesselExcursions = useMemo(() => {
      return excursions[vessel.id] || []
    }, [excursions, vessel.id]
  )

  return (
    <div className={`flex flex-col w-full gap-2 ${className}`}>
      <TrackedVesselMetric title="Total time fishing" value={1234} unit="time" />
      <TrackedVesselMetric title="MPA" value={123438} baseValue={2345} unit="time" />
      <TrackedVesselMetric title="French Territorial Waters" value={123438} baseValue={123439} unit="time" />
      <TrackedVesselMetric title="Zones with no fishing rights" value={1} baseValue={100} unit="time" />
      <TrackedVesselMetric title="AIS default" value={37.2} baseValue={100} unit="time" />
      {excursionsLoading ? (
        <Spinner />
      ) : (
        vesselExcursions.map((excursion, index) => (
          <TrackedVesselExcursion
            key={excursion.id}
            index={index + 1}
            excursion={excursion}
          />
        ))
      )}
    </div>
  )
}
