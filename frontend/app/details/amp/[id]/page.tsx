"use client"

import { useMemo, useState } from "react"
import { getZoneDetails } from "@/services/backend-rest-client"
import { swrOptions } from "@/services/swr"
import useSWR from "swr"

import { convertDurationInHours, format } from "@/libs/dateUtils"
import DetailsContainer from "@/components/details/details-container"

export default function AmpDetailsPage({ params }: { params: { id: string } }) {
  const [selectedDays, setSelectedDays] = useState(7)

  const { startAt, endAt } = useMemo(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const start = new Date(today)
    start.setDate(today.getDate() - selectedDays)
    return {
      startAt: format(start),
      endAt: format(today),
    }
  }, [selectedDays])

  const { data: zoneVisits = [], isLoading } = useSWR(
    [params.id, startAt, endAt],
    () => getZoneDetails(params.id, startAt, endAt).then((res) => res.data),
    swrOptions
  )

  const zoneDetails = useMemo(
    () =>
      zoneVisits[0]
        ? {
            id: zoneVisits[0].zone_id.toString(),
            label: zoneVisits[0].zone_name,
            description: zoneVisits[0].zone_sub_category,
            relatedItemsType: "Vessels",
            relatedItems: zoneVisits.map((visit) => ({
              id: visit.vessel_id.toString(),
              title: visit.vessel_name,
              description: `${visit.vessel_type} - ${visit.vessel_length_class}`,
              value: `${convertDurationInHours(
                visit.zone_visiting_time_by_vessel
              )}h`,
              type: "vessels",
            })),
          }
        : null,
    [zoneVisits]
  )

  return (
    <div className="h-screen">
      <DetailsContainer
        details={zoneDetails}
        onDateRangeChange={(value) => {
          setSelectedDays(Number(value))
        }}
        defaultDateRange={"7"}
        isLoading={isLoading}
      />
    </div>
  )
}
