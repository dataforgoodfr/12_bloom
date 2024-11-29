"use client"

import { useMemo, useState } from "react"
import { getZoneDetails } from "@/services/backend-rest-client"
import { swrOptions } from "@/services/swr"
import { getCountryNameFromIso3 } from "@/utils/vessel.utils"
import useSWR from "swr"

import { convertDurationInHours, getDateRange } from "@/libs/dateUtils"
import DetailsContainer from "@/components/details/details-container"

export default function AmpDetailsPage({ params }: { params: { id: string } }) {
  const [selectedDays, setSelectedDays] = useState(7)

  const { startAt, endAt } = useMemo(() => {
    return getDateRange(selectedDays)
  }, [selectedDays])

  const { data: zoneVisits = [], isLoading } = useSWR(
    [params.id, startAt, endAt],
    () => getZoneDetails(params.id, startAt, endAt).then((res) => res.data),
    swrOptions
  )

  const zoneDetails = useMemo(() => {
    if (!zoneVisits[0]) {
      return null
    }

    const { zone } = zoneVisits[0]
    return {
      id: zone.id.toString(),
      label: zone.name,
      description: zone.sub_category,
      relatedItemsType: "Vessels",
      relatedItems: zoneVisits.map((visit) => {
        const { vessel, zone_visiting_time_by_vessel } = visit
        return {
          id: vessel.id.toString(),
          title: `${vessel.ship_name} - ${getCountryNameFromIso3(vessel.country_iso3)}`,
          description: `IMO: ${vessel.imo} - MMSI: ${vessel.mmsi} - Type: ${vessel.type} - Length: ${vessel.length} m`,
          value: `${convertDurationInHours(zone_visiting_time_by_vessel)}h`,
          type: "vessels",
        }
      }),
    }
  }, [zoneVisits])

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
