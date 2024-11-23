"use client"

import { TOTAL_AMPS, TOTAL_VESSELS } from "@/constants/totals.constants"

import { Item } from "@/types/item"
import ListCard from "@/components/ui/list-card"
import KPICard from "@/components/dashboard/kpi-card"

import { DateRangeSelector } from "../ui/date-range-selector"

type Props = {
  topVesselsInActivity: Item[]
  topVesselsInActivityLoading: boolean
  topAmpsVisited: Item[]
  topAmpsVisitedLoading: boolean
  totalVesselsActive: number
  totalVesselsActiveLoading: boolean
  totalAmpsVisited: number
  totalAmpsVisitedLoading: boolean
  totalVesselsTracked: number
  totalVesselsTrackedLoading: boolean
  onDateRangeChange: (value: string) => void
}

export default function DashboardOverview({
  topVesselsInActivity,
  topVesselsInActivityLoading,
  topAmpsVisited,
  topAmpsVisitedLoading,
  totalVesselsActive,
  totalVesselsActiveLoading,
  totalAmpsVisited,
  totalAmpsVisitedLoading,
  totalVesselsTracked,
  totalVesselsTrackedLoading,
  onDateRangeChange,
}: Props) {
  return (
    <section className="grid">
      <div className="py-2 xl:py-4">
        <DateRangeSelector onValueChange={onDateRangeChange} defaultValue="7" />
      </div>

      <div className="grid grid-cols-3 gap-x-2 xl:gap-x-8">
        <div className="col-span-1 h-full">
          <div className="grid grid-cols-1 gap-y-2 xl:gap-y-8">
            <KPICard
              key="total-vessels-in-activity"
              title="Total vessels in Activity"
              kpiValue={totalVesselsActive}
              totalValue={totalVesselsTracked}
              loading={totalVesselsActiveLoading || totalVesselsTrackedLoading}
            />
            <KPICard
              key="total-amps-visited"
              title="Total AMPs visited"
              kpiValue={totalAmpsVisited}
              totalValue={TOTAL_AMPS}
              loading={totalAmpsVisitedLoading}
            />
          </div>
        </div>

        <div className="col-span-2 h-full">
          <div className="grid grid-cols-1 gap-y-12 xl:gap-y-16">
            <ListCard
              key="top-amps-visited"
              title="Top AMPs visited during the period"
              items={topAmpsVisited ?? []}
              enableViewDetails
              loading={topAmpsVisitedLoading}
              titleClassName="absolute -top-8 xl:-top-10"
            />
            <ListCard
              key="top-vessels-in-activity"
              title="Top Vessels visiting AMPS"
              items={topVesselsInActivity ?? []}
              enableViewDetails
              loading={topVesselsInActivityLoading}
              titleClassName="absolute -top-8 xl:-top-10"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
