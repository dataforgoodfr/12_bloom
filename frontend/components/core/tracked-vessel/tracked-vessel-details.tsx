"use client"

import TrackedVesselMetric from "./tracked-vessel-metric"
import { Vessel, VesselExcursion } from "@/types/vessel"
import TrackedVesselExcursion from "./tracked-vessel-excursion"

export interface TrackedVesselDetailsProps {
  vessel: Vessel
  onExcursionView: (excursion: VesselExcursion) => void
  onExcursionFocus: (excursion: VesselExcursion) => void
  className?: string
}

export default function TrackedVesselDetails({
  vessel,
  onExcursionView,
  onExcursionFocus,
  className,
}: TrackedVesselDetailsProps) {
  return (
    <div className={`flex flex-col w-full gap-2 ${className}`}>
      <TrackedVesselMetric title="Total time fishing" value={1234} unit="time" />
      <TrackedVesselMetric title="MPA" value={123438} baseValue={2345} unit="time" />
      <TrackedVesselMetric title="French Territorial Waters" value={123438} baseValue={123439} unit="time" />
      <TrackedVesselMetric title="Zones with no fishing rights" value={1} baseValue={100} unit="time" />
      <TrackedVesselMetric title="AIS default" value={37.2} baseValue={100} unit="time" />
      {vessel.excursions_timeframe?.excursions.map((excursion, index) => (
        <TrackedVesselExcursion
          key={excursion.id}
          index={index + 1}
          excursion={excursion}
          onView={() => onExcursionView(excursion)}
          onFocus={() => onExcursionFocus(excursion)}
        />
      ))}
    </div>
  )
}
