"use client"

import { useEffect, useState } from "react"

import { Item } from "@/types/item"
import { VesselTrackingTimeDto } from "@/types/vessel"
import { ZoneVisitTimeDto } from "@/types/zone"
import { convertVesselDtoToItem, convertZoneDtoToItem } from "@/libs/mapper"
import Dropdown from "@/components/ui/dropdown"
import ListCard from "@/components/ui/list-card"
import KPICard from "@/components/dashboard/kpi-card"

const TOTAL_VESSELS = 1700
const TOTAL_AMPS = 720

type Props = {
  topVesselsInActivity: VesselTrackingTimeDto[]
  topAmpsVisited: ZoneVisitTimeDto[]
  totalVesselsActive: number
  totalAmpsVisited: number
}

export default function DashboardOverview(props: Props) {
  const {
    topVesselsInActivity,
    topAmpsVisited,
    totalVesselsActive,
    totalAmpsVisited,
  } = props
  const [vesselsItems, setVesselsItems] = useState<Item[]>([])
  const [ampsItems, setAmpsItems] = useState<Item[]>([])

  useEffect(() => {
    // Move data transformations into useEffect
    if (topVesselsInActivity) {
      const transformedVessels = convertVesselDtoToItem(topVesselsInActivity)
      setVesselsItems(transformedVessels)
    }

    if (topAmpsVisited) {
      const transformedAmps = convertZoneDtoToItem(topAmpsVisited)
      setAmpsItems(transformedAmps)
    }
  }, [topVesselsInActivity, topAmpsVisited])

  return (
    <section className="grid">
      <div className="mb-2 w-full">
        <Dropdown
          className="float-right w-40"
          options={["360 derniers jours"]}
          onSelect={(value) => console.log("selected: " + value)}
        />
      </div>

      <div className="grid grid-cols-3 gap-x-3">
        <div className="col-span-1 h-full">
          <div className="grid grid-cols-1 gap-y-2">
            <KPICard
              title="Total vessels in Activity"
              kpiValue={totalVesselsActive}
              totalValue={TOTAL_VESSELS}
            />
            <KPICard
              title="Total AMPs visited"
              kpiValue={totalAmpsVisited}
              totalValue={TOTAL_AMPS}
            />
          </div>
        </div>

        <div className="col-span-2 h-full">
          <div className="grid grid-cols-1 gap-y-4">
            <ListCard
              title="Top AMPs visited during the period"
              items={ampsItems ?? []}
              enableViewDetails
            />
            <ListCard
              title="Top Vessels visiting AMPS"
              items={vesselsItems ?? []}
              enableViewDetails
            />
          </div>
        </div>
      </div>
    </section>
  )
}
