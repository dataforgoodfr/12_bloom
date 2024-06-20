"use client"

import { useState } from "react"
import allVessels from "@/public/data/geometries/all_vessels_with_mmsi.json"
import latestPositions from "@/public/data/geometries/vessels_latest_positions.json"
import { FlyToInterpolator } from "deck.gl"
import { ShipIcon } from "lucide-react"

import { Vessel } from "@/types/vessel"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import { useMapStore } from "@/components/providers/map-store-provider"

import { VesselPosition } from "../map/main-map"

type Props = {
  wideMode: boolean
}

const SEPARATOR = "___"

export function VesselFinderDemo({ wideMode }: Props) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState<string>("")
  const {
    addTrackedVesselMMSI,
    trackedVesselMMSIs,
    setActivePosition,
    viewState,
    setViewState,
  } = useMapStore((state) => state)

  const onSelectVessel = (vesselIdentifier: string) => {
    const mmsi = parseInt(vesselIdentifier.split(SEPARATOR)[1])
    if (mmsi && !trackedVesselMMSIs.includes(mmsi)) {
      addTrackedVesselMMSI(mmsi)
    }
    if (mmsi) {
      const selectedVesselLatestPosition = latestPositions.find(
        (position) => position.vessel_mmsi === mmsi
      )
      if (selectedVesselLatestPosition) {
        setActivePosition(selectedVesselLatestPosition as VesselPosition)
        setViewState({
          ...viewState,
          longitude: selectedVesselLatestPosition.position_longitude,
          latitude: selectedVesselLatestPosition.position_latitude,
          zoom: 7,
          pitch: 40,
          transitionInterpolator: new FlyToInterpolator({ speed: 2 }),
          transitionDuration: "auto",
        })
      }
    }
    setOpen(false)
  }

  return (
    <>
      <button
        type="button"
        className="dark:highlight-white/5 flex items-center rounded-md bg-color-3 py-1.5 pl-2 pr-3 text-sm leading-6 text-slate-400 shadow-sm ring-1 ring-color-2 hover:bg-slate-700 hover:ring-slate-300"
        onClick={() => setOpen(true)}
      >
        <svg
          width="24"
          height="24"
          fill="none"
          aria-hidden="true"
          className="mr-3 flex-none"
        >
          <path
            d="m19 19-3.5-3.5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></path>
          <circle
            cx="11"
            cy="11"
            r="6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></circle>
        </svg>
        {wideMode && <>Find vessels...</>}
      </button>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput
          placeholder="Type MMSI, IMO or vessel name to search..."
          value={search}
          onValueChange={setSearch}
        />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Vessels">
            {allVessels.map((vessel: Vessel) => {
              return (
                <CommandItem
                  key={`${vessel.imo}-${vessel.name}`}
                  onSelect={(value) => onSelectVessel(value)}
                  value={`${vessel.name}${SEPARATOR}${vessel.mmsi}${SEPARATOR}${vessel.imo}`} // so we can search by name, mmsi, imo
                >
                  <ShipIcon className="mr-2 size-4" />
                  <span>{vessel.name}</span>
                  <span className="ml-2 text-xxxs">
                    {" "}
                    MMSI {vessel.mmsi} | IMO {vessel.imo}
                  </span>
                </CommandItem>
              )
            })}
          </CommandGroup>
          <CommandSeparator />
        </CommandList>
      </CommandDialog>
    </>
  )
}
