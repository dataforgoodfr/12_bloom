"use client"

import mockData from "@/public/data/mock-data-dashboard.json"

import Dropdown from "@/components/ui/dropdown"
import ListCard from "@/components/ui/list-card"
import KPICard from "@/components/dashboard/kpi-card"

// TODO: use real data + load in server components
let amps = mockData["top-amps"]
let vessels = mockData["top-vessels"]
let totalVesselsActive = mockData["total-vessels-active"]
let totalVessels = mockData["total-vessels"]
let totalAmpsVisited = mockData["total-amps-visited"]
let totalAmps = mockData["total-amps"]
let fishingEffort = mockData["fishing-effort-hours"]
let fishingArea = mockData["fishing-area-km2"]

export default function DashboardOverview() {
  return (
    <section className="grid">
      <div className="mb-2 w-full">
        <Dropdown
          className="float-right w-40"
          options={["7 derniers jours", "30 derniers jours"]} // TODO: move in dedicated enum?
          onSelect={(value) => console.log("selected: " + value)}
        />
      </div>

      <div className="grid grid-cols-3 gap-x-3">
        <div className="col-span-1 h-full">
          <div className="grid grid-cols-1 gap-y-2">
            <KPICard
              title="Total vessels in Activity"
              kpiValue={totalVesselsActive}
              totalValue={totalVessels}
            />
            <KPICard
              title="Total AMPs visited"
              kpiValue={totalAmpsVisited}
              totalValue={totalAmps}
            />
            <KPICard
              title="Fishing effort"
              kpiValue={fishingEffort}
              kpiUnit="Hours"
              totalValue={fishingArea}
              totalUnit="Km2"
            />
          </div>
        </div>

        <div className="col-span-2 h-full">
          <div className="grid grid-cols-1 gap-y-4">
            <ListCard
              title="Top AMPs visited during the period"
              items={amps}
              enableViewDetails
            />
            <ListCard
              title="Top Vessels visiting AMPS"
              items={vessels}
              enableViewDetails
            />
          </div>
        </div>
      </div>
    </section>
  )
}
