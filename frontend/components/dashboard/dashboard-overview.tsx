"use client"

import Dropdown from "@/components/ui/dropdown"
import ListCard from "@/components/ui/list-card"
import KPICard from "@/components/dashboard/kpi-card"
import { ZoneVisitTimeDto } from "@/types/zone"
import { VesselTrackingTimeDto } from "@/types/vessel"
import { convertVesselDtoToItem, convertZoneDtoToItem } from "@/libs/mapper";

const TOTAL_VESSELS = 1700;
const TOTAL_AMPS = 720;

type Props = {
  topVesselsInActivity: VesselTrackingTimeDto[];
  topAmpsVisited: ZoneVisitTimeDto[];
  totalVesselsActive: number;
  totalAmpsVisited: number;
}

export default function DashboardOverview(props : Props) {
  const { topVesselsInActivity, topAmpsVisited, totalVesselsActive, totalAmpsVisited } = props;
  const topVesselsInActivityToItems = convertVesselDtoToItem(topVesselsInActivity);
  const topAmpsVisitedToItems = convertZoneDtoToItem(topAmpsVisited);

  return (
    <section className="grid">
      <div className="mb-2 w-full">
        <Dropdown
          className="float-right w-40"
          options={["360 derniers jours"]} // TODO: move in dedicated enum?
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
              items={topAmpsVisitedToItems ?? []}
              enableViewDetails
            />
            <ListCard
              title="Top Vessels visiting AMPS"
              items={topVesselsInActivityToItems ?? []}
              enableViewDetails
            />
          </div>
        </div>
      </div>
    </section>
  )
}
