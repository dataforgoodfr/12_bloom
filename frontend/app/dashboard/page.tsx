"use client"

import { useMemo, useState } from "react"
import {
  getTopVesselsInActivity,
  getTopZonesVisited,
} from "@/services/backend-rest-client"
import { swrOptions } from "@/services/swr"
import useSWR from "swr"

import { getDateRange } from "@/libs/dateUtils"
import { convertVesselDtoToItem, convertZoneDtoToItem } from "@/libs/mapper"
import DashboardHeader from "@/components/dashboard/dashboard-header"
import DashboardOverview from "@/components/dashboard/dashboard-overview"

const TOP_ITEMS_SIZE = 5

async function fetchTopVesselsInActivity(startAt: string, endAt: string) {
  try {
    const response = await getTopVesselsInActivity(
      startAt,
      endAt,
      TOP_ITEMS_SIZE
    )
    return convertVesselDtoToItem(response?.data || [])
  } catch (error) {
    console.log(
      "An error occured while fetching top vessels in activity : " + error
    )
    return []
  }
}

async function fetchTopAmpsVisited(startAt: string, endAt: string) {
  try {
    const response = await getTopZonesVisited(startAt, endAt, TOP_ITEMS_SIZE)
    return convertZoneDtoToItem(response?.data || [])
  } catch (error) {
    console.log("An error occured while fetching top amps visited: " + error)
    return []
  }
}

async function fetchTotalVesselsInActivity(startAt: string, endAt: string) {
  try {
    // TODO(CT): replace with new endpoint (waiting for Hervé)
    const response = await getTopVesselsInActivity(startAt, endAt, 1700) // high value to capture all data
    return response?.data?.length
  } catch (error) {
    console.log("An error occured while fetching top amps visited: " + error)
    return 0
  }
}

async function fetchTotalAmpsVisited(startAt: string, endAt: string) {
  try {
    // TODO(CT): replace with new endpoint (waiting for Hervé)
    const response = await getTopZonesVisited(startAt, endAt, 100000) // high value to capture all data
    return response?.data?.length
  } catch (error) {
    console.log("An error occured while fetching top amps visited: " + error)
    return 0
  }
}

export default function DashboardPage() {
  const [selectedDays, setSelectedDays] = useState(7)
  const { startAt, endAt } = useMemo(() => {
    return getDateRange(selectedDays)
  }, [selectedDays])

  const {
    data: topVesselsInActivity = [],
    isLoading: topVesselsInActivityLoading,
  } = useSWR(
    `topVesselsInActivity-${startAt}-${endAt}`,
    () => fetchTopVesselsInActivity(startAt, endAt),
    swrOptions
  )

  const { data: topAmpsVisited = [], isLoading: topAmpsVisitedLoading } =
    useSWR(
      `topAmpsVisited-${startAt}-${endAt}`,
      () => fetchTopAmpsVisited(startAt, endAt),
      swrOptions
    )

  const {
    data: totalVesselsInActivity = 0,
    isLoading: totalVesselsInActivityLoading,
  } = useSWR(
    `totalVesselsInActivity-${startAt}-${endAt}`,
    () => fetchTotalVesselsInActivity(startAt, endAt),
    swrOptions
  )

  const { data: totalAmpsVisited = 0, isLoading: totalAmpsVisitedLoading } =
    useSWR(
      `totalAmpsVisited-${startAt}-${endAt}`,
      () => fetchTotalAmpsVisited(startAt, endAt),
      swrOptions
    )

  return (
    <section className="flex h-full items-center justify-center overflow-auto bg-color-3 p-2 2xl:p-4">
      <div className="flex size-full max-w-screen-xl flex-col gap-2 2xl:gap-4">
        <div className="block h-[45px] w-full">
          <DashboardHeader />
        </div>

        <div className="size-full">
          <DashboardOverview
            topVesselsInActivity={topVesselsInActivity}
            topAmpsVisited={topAmpsVisited}
            totalVesselsActive={totalVesselsInActivity}
            totalAmpsVisited={totalAmpsVisited}
            onDateRangeChange={(value) => {
              setSelectedDays(Number(value))
            }}
            topVesselsInActivityLoading={topVesselsInActivityLoading}
            topAmpsVisitedLoading={topAmpsVisitedLoading}
            totalVesselsActiveLoading={totalVesselsInActivityLoading}
            totalAmpsVisitedLoading={totalAmpsVisitedLoading}
          />
        </div>
      </div>
    </section>
  )
}
