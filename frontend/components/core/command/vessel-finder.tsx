"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { getVesselFirstExcursionSegments } from "@/services/backend-rest-client"
import { FlyToInterpolator } from "deck.gl"
import { useShallow } from "zustand/react/shallow"

import { VesselPosition } from "@/types/vessel"
import { useMapStore } from "@/libs/stores/map-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { useVesselsStore } from "@/libs/stores/vessels-store"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"

type Props = {
  wideMode: boolean
  setWideMode: (wideMode: boolean) => void
}

const SEPARATOR = "___"

export function VesselFinderDemo({ wideMode, setWideMode }: Props) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState<string>("")
  const inputRef = useRef<HTMLInputElement>(null)

  const { addTrackedVessel, trackedVesselIDs } = useTrackModeOptionsStore(
    useShallow((state) => ({
      addTrackedVessel: state.addTrackedVessel,
      trackedVesselIDs: state.trackedVesselIDs,
    }))
  )

  const { setActivePosition, viewState, latestPositions, setViewState } =
    useMapStore(
      useShallow((state) => ({
        viewState: state.viewState,
        latestPositions: state.latestPositions,
        setActivePosition: state.setActivePosition,
        setViewState: state.setViewState,
      }))
    )

  const { vessels: allVessels } = useVesselsStore(
    useShallow((state) => ({
      vessels: state.vessels,
    }))
  )

  const simpleVessels = useMemo(() => {
    return allVessels.map((vessel) => ({
      id: vessel.id,
      title: vessel.ship_name,
      subtitle: `MMSI ${vessel.mmsi} | IMO ${vessel.imo}`,
      value: `${vessel.ship_name}${SEPARATOR}${vessel.mmsi}${SEPARATOR}${vessel.imo}${SEPARATOR}${vessel.id}`,
    }))
  }, [allVessels])

  const filteredItems = useMemo(
    () =>
      simpleVessels.filter(
        (vessel) =>
          vessel.value.toLowerCase().includes(search.toLowerCase()) &&
          !trackedVesselIDs.includes(vessel.id)
      ),
    [simpleVessels, search, trackedVesselIDs]
  )

  useEffect(() => {
    if (!wideMode && open) {
      setOpen(false)
    }
  }, [wideMode])

  const displayedItems = filteredItems.slice(0, 50)

  const onSelectVessel = async (vesselIdentifier: string) => {
    setOpen(false)
    const vesselId = parseInt(vesselIdentifier.split(SEPARATOR)[3])

    const response = await getVesselFirstExcursionSegments(vesselId)
    if (vesselId && !trackedVesselIDs.includes(vesselId)) {
      addTrackedVessel(vesselId)
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
    <Command
      className={`relative overflow-visible border-[0.5px] border-color-panel border-solid ${!wideMode ? "cursor-pointer hover:border-primary hover:text-primary" : "cursor-default"} ${open ? "rounded-t-lg rounded-b-none" : "rounded-lg"}`}
      onClick={() => {
        if (!wideMode) {
          setWideMode(true)
          setOpen(true)
          inputRef.current?.focus()
        }
      }}
    >
      <CommandInput
        ref={inputRef}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => setOpen(true)}
        onValueChange={(value) => setSearch(value)}
        placeholder="Type MMSI, IMO or vessel name to search..."
      />
      <CommandList
        className="absolute -left-[.5px] top-[calc(100%)] z-[100] w-full rounded-bl-md  bg-background shadow-md border-[.5px] border-color-panel"
        hidden={!open}
        onMouseDown={(e) => {
          e.preventDefault()
        }}
      >
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Vessels">
          {displayedItems.map((vessel) => {
            return (
              <CommandItem
                className="border-none"
                key={`${vessel.id}`}
                onSelect={(value) => onSelectVessel(value)}
                value={vessel.value}
              >
                <div className="flex flex-wrap items-baseline gap-1">
                  <span>{vessel.title}</span>
                  <span>-</span>
                  <span className="text-xxs text-neutral-300">
                    {vessel.subtitle}
                  </span>
                </div>
              </CommandItem>
            )
          })}
        </CommandGroup>
        <CommandSeparator />
      </CommandList>
    </Command>
  )
}
