"use client"

import { useEffect, useMemo, useState } from "react"
import { PopoverContent, PopoverTrigger } from "@radix-ui/react-popover"
import { format } from "date-fns"
import {
  CalendarIcon,
  ChevronRight,
  MinusIcon,
  PenIcon,
  Ship as ShipIcon,
  XIcon,
} from "lucide-react"

import { Vessel } from "@/types/vessel"
import { cn } from "@/libs/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover } from "@/components/ui/popover"
import { useMapStore } from "@/components/providers/map-store-provider"
import { useVesselsStore } from "@/components/providers/vessels-store-provider"

import TrackedVesselItem from "./tracked-vessel-item"

type Props = {
  wideMode: boolean
  parentIsOpen: boolean
  openParent: () => void
}

function NoVesselsPlaceholder() {
  return (
    <p className="flex items-center rounded-md py-1.5 pl-1 pr-3 text-sm leading-6 text-slate-400">
      <span>There is no vessels selected</span>
    </p>
  )
}

function VesselsActions({
  onCreateFleet = () => {},
  disabledCreateFleet = false,
  onViewTracks = () => {},
  disabledViewTracks = false,
}: {
  onCreateFleet?: () => void
  disabledCreateFleet?: boolean
  onViewTracks?: () => void
  disabledViewTracks?: boolean
}) {
  return (
    <div className="flex justify-center gap-1">
      <Button
        variant="outline"
        onClick={onCreateFleet}
        disabled={disabledCreateFleet}
        className="border border-color-1 bg-inherit text-color-1"
        color="primary"
      >
        <PenIcon className="size-4" />
        Create fleet
      </Button>
      <Button
        onClick={onViewTracks}
        disabled={disabledViewTracks}
        color="primary"
      >
        View tracks
        <ChevronRight className="size-4" />
      </Button>
    </div>
  )
}

function TrackModeDatePicker({
  date,
  setDate,
  maxDate,
  minDate,
}: {
  date: Date | undefined
  setDate: (date: Date | undefined) => void
  maxDate?: Date
  minDate?: Date
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "justify-start text-left font-normal bg-popover",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "PPP") : <span className="">Pick a date</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={setDate}
          initialFocus
          className="bg-white"
          toDate={maxDate}
          fromDate={minDate}

        />
      </PopoverContent>
    </Popover>
  )
}

function TrackModeHeader({
  startDate,
  setStartDate,
  endDate,
  setEndDate,
}: {
  startDate: Date | undefined
  setStartDate: (date: Date | undefined) => void
  endDate: Date | undefined
  setEndDate: (date: Date | undefined) => void
}) {
  const { setMode: setMapMode } = useMapStore((state) => state)
  const today = new Date()

  const minDate = useMemo(() => {
    return startDate ? startDate : today
  }, [startDate])

  const onSetStartDate = (date: Date | undefined) => {
    setStartDate(date)
    if (date && endDate && date > endDate) {
      setEndDate(undefined)
    }
  }

  const onSetEndDate = (date: Date | undefined) => {
    setEndDate(date)
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h5 className="font-bold uppercase leading-6">TRACK MODE</h5>
        <XIcon
          className="size-6 cursor-pointer hover:text-color-1"
          onClick={() => setMapMode("position")}
        />
      </div>
      <div className="flex justify-between">
        <div className="flex justify-center items-center">
          <TrackModeDatePicker
            date={startDate}
            setDate={onSetStartDate}
            maxDate={today}
          />
          <MinusIcon className="size-4 text-color-1 mx-2" />
          <TrackModeDatePicker
            date={endDate}
            setDate={onSetEndDate}
            maxDate={today}
            minDate={minDate}
          />
        </div>
      </div>
    </div>
  )
}

export default function TrackedVesselsPanel({
  wideMode,
  parentIsOpen,
  openParent,
}: Props) {
  const {
    trackedVesselIDs,
    removeTrackedVessel,
    mode: mapMode,
    setMode: setMapMode,
  } = useMapStore((state) => state)
  const { vessels: allVessels } = useVesselsStore((state) => state)
  const [displayTrackedVessels, setDisplayTrackedVessels] = useState(false)
  const [trackedVesselsDetails, setTrackedVesselsDetails] = useState<Vessel[]>()

  const [startDate, setStartDate] = useState<Date | undefined>()
  const [endDate, setEndDate] = useState<Date | undefined>()

  const showOrHideTrackedVessels = () => {
    if (!parentIsOpen) {
      openParent()
    }
    setDisplayTrackedVessels(!displayTrackedVessels)
  }

  useEffect(() => {
    const vesselsDetails = allVessels.filter((vessel) =>
      trackedVesselIDs.includes(vessel.id)
    )
    setTrackedVesselsDetails(vesselsDetails)
  }, [allVessels, trackedVesselIDs])

  const hasTrackedVessels = useMemo(() => {
    return trackedVesselIDs.length > 0
  }, [trackedVesselIDs])

  const onRemoveVesselTracked = (vesselID: number) => {
    removeTrackedVessel(vesselID)
  }

  const onViewTracks = () => {
    setMapMode("excursion")
  }

  const WideModeTab = () => {
    return (
      <>
        {mapMode === "excursion" && (
          <TrackModeHeader
            startDate={startDate}
            setStartDate={setStartDate}
            endDate={endDate}
            setEndDate={setEndDate}
          />
        )}
        {!hasTrackedVessels && <NoVesselsPlaceholder />}

        {trackedVesselsDetails?.map((vessel: Vessel, index) => {
          return (
            <TrackedVesselItem
              key={vessel.id}
              showDetails={mapMode === "excursion"}
              vessel={vessel}
              colorIndex={index}
              onRemove={onRemoveVesselTracked}
              onView={() => {}}
              className={`${
                index < allVessels.slice(10, 20).length - 1
                  ? "border-b border-color-3"
                  : ""
              }`}
            />
          )
        })}

        {mapMode === "position" && (
          <VesselsActions
            disabledCreateFleet={true}
            onViewTracks={onViewTracks}
            disabledViewTracks={!hasTrackedVessels}
          />
        )}
      </>
    )
  }

  return (
    <>
      <div>
        <h5
          className="flex gap-1 text-sm font-bold uppercase leading-6"
          onClick={() => showOrHideTrackedVessels()}
        >
          {!wideMode && <ShipIcon className="w-8 min-w-8" />}
          {mapMode === "position" && wideMode && (
            <span>{`Selected vessel (${trackedVesselIDs.length})`}</span>
          )}
        </h5>
      </div>

      {wideMode && <WideModeTab />}
    </>
  )
}
