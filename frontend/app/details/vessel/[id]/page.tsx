"use client"

import { useMemo, useState } from "react"
import Image from "next/image"
import { getTimeByZone } from "@/services/backend-rest-client"
import { getCountryNameFromIso3 } from "@/utils/vessel.utils"
import useSWR from "swr"

import { convertDurationToString, getDateRange } from "@/libs/dateUtils"
import DetailsContainer from "@/components/details/details-container"

export default function VesselDetailsPage({
  params,
}: {
  params: { id: string }
}) {
  const [selectedDays, setSelectedDays] = useState(7)

  const { startAt, endAt } = useMemo(() => {
    return getDateRange(selectedDays)
  }, [selectedDays])

  const { data: zonesVisited = [], isLoading } = useSWR(
    [params.id, startAt, endAt],
    () =>
      getTimeByZone(startAt, endAt, 10, "amp", params.id).then(
        (res) => res.data
      ),
    {
      revalidateOnMount: true,
      keepPreviousData: true,
    }
  )

  const vesselDetails = useMemo(() => {
    if (!zonesVisited[0]) {
      return null
    }

    const { vessel } = zonesVisited[0]
    return {
      id: vessel.id.toString(),
      label: `${vessel.ship_name} - ${getCountryNameFromIso3(vessel.country_iso3)}`,
      description: `IMO: ${vessel.imo} - MMSI: ${vessel.mmsi} - Type: ${vessel.type} - Length: ${vessel.length} m`,
      relatedItemsType: "Zones",
      relatedItems: zonesVisited.map((visit) => {
        const { zone, vessel_visiting_time_by_zone } = visit
        return {
          id: zone.id.toString(),
          title: zone.name,
          description: zone.sub_category,
          value: convertDurationToString(vessel_visiting_time_by_zone),
          type: "zones",
        }
      }),
    }
  }, [zonesVisited])

  return (
    <div className="h-screen">
      <DetailsContainer
        details={vesselDetails}
        type="vessel"
        onDateRangeChange={(value) => {
          setSelectedDays(Number(value))
        }}
        defaultDateRange={"7"}
        isLoading={isLoading}
      >
        <Image
          src="/img/scrombus.jpg"
          alt="Vessel image"
          className="object-cover"
          fill
        />
      </DetailsContainer>
    </div>
  )
}
