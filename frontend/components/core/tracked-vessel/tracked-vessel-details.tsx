"use client"

import { useMemo } from "react"
import { useShallow } from "zustand/react/shallow"

import { Vessel, VesselExcursion, ExcursionMetrics } from "@/types/vessel"
import { convertDurationInSeconds, formatDuration } from "@/libs/dateUtils"
import { useLoaderStore } from "@/libs/stores/loader-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import Spinner from "@/components/ui/custom/spinner"

import TrackedVesselExcursion from "./tracked-vessel-excursion"
import TrackedVesselMetric from "./tracked-vessel-metric"

export interface TrackedVesselDetailsProps {
  vessel: Vessel
  className?: string
}

export default function TrackedVesselDetails({
  vessel,
  className,
}: TrackedVesselDetailsProps) {
  const { excursions } = useTrackModeOptionsStore(
    useShallow((state) => ({
      excursions: state.excursions,
    }))
  )

  const { excursionsLoading } = useLoaderStore(
    useShallow((state) => ({
      excursionsLoading: state.excursionsLoading,
    }))
  )

  const vesselExcursions = useMemo(() => {
    return excursions[vessel.id] || []
  }, [excursions, vessel.id])

  const computeExcursionMetrics = (
    excursions: VesselExcursion[]
  ): ExcursionMetrics => {
    const metrics: ExcursionMetrics = {
      totalTimeAtSea: 0,
      mpa: 0,
      frenchTerritorialWaters: 0,
      zonesWithNoFishingRights: 0,
      aisDefault: 0,
    }
    for (const excursion of excursions) {
      metrics.totalTimeAtSea += convertDurationInSeconds(
        excursion.excursion_duration
      )
      metrics.mpa += convertDurationInSeconds(excursion.total_time_in_amp)
      metrics.frenchTerritorialWaters += convertDurationInSeconds(
        excursion.total_time_in_territorial_waters
      )
      metrics.zonesWithNoFishingRights += convertDurationInSeconds(
        excursion.total_time_in_zones_with_no_fishing_rights
      )
      metrics.aisDefault += convertDurationInSeconds(
        excursion.total_time_default_ais
      )
    }
    return metrics
  }

  const excursionsMetrics = useMemo(() => {
    return computeExcursionMetrics(vesselExcursions)
  }, [vesselExcursions])

  if (excursionsLoading) {
    return <Spinner />
  }

  return (
    <div className={`flex w-full flex-col gap-2 ${className}`}>
      <TrackedVesselMetric
        title="Total time at sea"
        value={excursionsMetrics.totalTimeAtSea}
        unit="time"
      />
      <TrackedVesselMetric
        title="MPA"
        value={excursionsMetrics.mpa}
        baseValue={excursionsMetrics.totalTimeAtSea}
        unit="time"
      />
      <TrackedVesselMetric
        title="French Territorial Waters"
        value={excursionsMetrics.frenchTerritorialWaters}
        baseValue={excursionsMetrics.totalTimeAtSea}
        unit="time"
      />
      <TrackedVesselMetric
        title="Zones with no fishing rights"
        value={excursionsMetrics.zonesWithNoFishingRights}
        baseValue={excursionsMetrics.totalTimeAtSea}
        unit="time"
      />
      <TrackedVesselMetric
        title="AIS default"
        value={excursionsMetrics.aisDefault}
        baseValue={excursionsMetrics.totalTimeAtSea}
        unit="time"
      />
      {vesselExcursions.map((excursion, index) => (
        <TrackedVesselExcursion
          key={excursion.id}
          index={index + 1}
          excursion={excursion}
        />
      ))}
    </div>
  )
}
