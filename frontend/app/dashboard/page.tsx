"use client"

import { useMemo, useState } from "react"
import { useDashboardData } from "@/services/dashboard.service"

import { getDateRange } from "@/libs/dateUtils"
import DashboardHeader from "@/components/dashboard/dashboard-header"
import DashboardOverview from "@/components/dashboard/dashboard-overview"

export default function DashboardPage() {
  const [selectedDays, setSelectedDays] = useState(7)
  const { startAt, endAt } = useMemo(() => {
    return getDateRange(selectedDays)
  }, [selectedDays])

  const {
    topVesselsInActivity,
    topAmpsVisited,
    totalVesselsInActivity,
    totalAmpsVisited,
    totalVesselsTracked,
    isLoading,
  } = useDashboardData(startAt, endAt)

  console.log("totalVesselsTracked", totalVesselsTracked)

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
            totalVesselsTracked={totalVesselsTracked}
            onDateRangeChange={(value) => {
              setSelectedDays(Number(value))
            }}
            topVesselsInActivityLoading={isLoading.topVesselsInActivity}
            topAmpsVisitedLoading={isLoading.topAmpsVisited}
            totalVesselsActiveLoading={isLoading.totalVesselsInActivity}
            totalAmpsVisitedLoading={isLoading.totalAmpsVisited}
            totalVesselsTrackedLoading={isLoading.totalVesselsTracked}
          />
        </div>
      </div>
    </section>
  )
}
