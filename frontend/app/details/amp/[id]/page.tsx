"use client"

import { useEffect, useMemo, useState } from "react"
import { getZoneDetails } from "@/services/backend-rest-client"

import { ItemDetails } from "@/types/item"
import { ZoneVisits } from "@/types/zone"
import { convertDurationInHours, format } from "@/libs/dateUtils"
import { convertZoneDtoToItem } from "@/libs/mapper"
import DetailsContainer from "@/components/details/details-container"

export default function AmpDetailsPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { days?: string }
}) {
  const [selectedDays, setSelectedDays] = useState(
    Number(searchParams.days) || 7
  )
  const [zoneVisits, setZoneVisits] = useState<ZoneVisits[]>([])
  const [isLoading, setIsLoading] = useState(true)

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

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      const { data } = await getZoneDetails(params.id, startAt, endAt)
      setZoneVisits(data)
      setIsLoading(false)
    }
    fetchData()
  }, [params.id, startAt, endAt])

  // Convert zoneVisits to ItemDetails
  const zoneDetails: ItemDetails | null = zoneVisits[0]
    ? {
        id: zoneVisits[0].zone_id.toString(),
        label: zoneVisits[0].zone_name,
        description: zoneVisits[0].zone_sub_category,
        relatedItemsType: "Vessels",
        relatedItems: zoneVisits.map((visit) => ({
          id: visit.vessel_id.toString(),
          title: visit.vessel_name,
          description: visit.vessel_type,
          value: `${convertDurationInHours(
            visit.zone_visiting_time_by_vessel
          )}h`,
          type: "vessels",
        })),
      }
    : null

  return (
    <div className="h-full">
      <DetailsContainer
        details={zoneDetails}
        onDateRangeChange={(value) => {
          setSelectedDays(Number(value))
        }}
        defaultDateRange={searchParams.days || "7"}
        isLoading={isLoading}
      />
    </div>
  )
}
