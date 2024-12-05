"use client";

import { useState } from "react";
import { getVesselExcursionSegments } from "@/services/backend-rest-client"
import { FlyToInterpolator } from "deck.gl";



import { Vessel, VesselPosition } from "@/types/vessel";
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from "@/components/ui/command";
import { useMapStore } from "@/components/providers/map-store-provider";
import { useVesselsStore } from "@/components/providers/vessels-store-provider";





type Props = {
  wideMode: boolean
}

const SEPARATOR = "___"

export function VesselFinderDemo({ wideMode }: Props) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState<string>("")
  const {
    addTrackedVessel,
    trackedVesselIDs,
    setActivePosition,
    viewState,
    setViewState,
  } = useMapStore((state) => state)
  const { vessels: allVessels } = useVesselsStore((state) => state)
  const { latestPositions } = useMapStore((state) => state)

  const onSelectVessel = async (vesselIdentifier: string) => {
    const vesselId = parseInt(vesselIdentifier.split(SEPARATOR)[3])
    const response = await getVesselExcursionSegments(vesselId, "2024-12-02", "2024-12-05")
    if (vesselId && !trackedVesselIDs.includes(vesselId)) {
      addTrackedVessel(vesselId, response)
    }
    if (vesselId) {
      const selectedVesselLatestPosition = latestPositions.find(
        (position) => position.vessel.id === vesselId
      )
      if (selectedVesselLatestPosition) {
        setActivePosition(selectedVesselLatestPosition as VesselPosition)
        setViewState({
          ...viewState,
          longitude: selectedVesselLatestPosition.position.coordinates[0],
          latitude: selectedVesselLatestPosition.position.coordinates[1],
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
                  key={`${vessel.id}`}
                  onSelect={(value) => onSelectVessel(value)}
                  value={`${vessel.ship_name}${SEPARATOR}${vessel.mmsi}${SEPARATOR}${vessel.imo}${SEPARATOR}${vessel.id}`} // so we can search by name, mmsi, imo
                >
                  <span>{vessel.ship_name}</span>
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