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
import { DayPicker, getDefaultClassNames, Matcher } from "react-day-picker"

import { Vessel } from "@/types/vessel"
import { cn } from "@/libs/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Popover } from "@/components/ui/popover"
import { useMapStore } from "@/components/providers/map-store-provider"
import { useVesselsStore } from "@/components/providers/vessels-store-provider"

import TrackedVesselItem from "./tracked-vessel-item"

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
      >
        <PenIcon className="size-4" />
        Create fleet
      </Button>
      <Button onClick={onViewTracks} disabled={disabledViewTracks}>
        View tracks
        <ChevronRight className="size-4" />
      </Button>
    </div>
  )
}

function TrackModeDatePicker({
  label,
  date,
  setDate,
  maxDate,
  minDate,
  className,
}: {
  label: string
  date: Date | undefined
  setDate: (date: Date | undefined) => void
  maxDate?: Date
  minDate?: Date
  className?: string
}) {
  const defaultClassNames = getDefaultClassNames()
  const disabledMatchers: Matcher[] = []

  if (minDate) {
    disabledMatchers.push({ before: minDate })
  }

  if (maxDate) {
    disabledMatchers.push({ after: maxDate })
  }

  const onClear = () => {
    setDate(undefined)
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "justify-start bg-white text-left font-normal !text-color-2 shadow-md hover:border-color-1 hover:bg-white",
            !date && "text-muted-foreground",
            className
          )}
          color="primary"
        >
          <CalendarIcon className="mr-2 size-4" />
          {date ? (
            format(date, "dd/MM/yyyy")
          ) : (
            <span className="">{label}</span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="z-10 w-auto p-0">
        <DayPicker
          mode="single"
          selected={date}
          onSelect={setDate}
          classNames={{
            root: `${defaultClassNames.root} bg-white rounded-md`,
            selected: `bg-color-1 rounded-md`,
            today: `text-color-1`,
            chevron: `fill-color-1`,
            disabled: `${defaultClassNames.disabled} text-muted-foreground hover:bg-transparent`,
            day: `text-color-2 hover:bg-color-1/20 rounded-md`,
            month_caption: `text-color-2 p-3`,
            weekdays: `text-color-2`,
          }}
          footer={
            <div className="flex justify-center gap-1 p-4">
              <Button
                variant="outline"
                onClick={onClear}
                disabled={!date}
                className="h-8 border-color-1 bg-white text-color-1 hover:border-color-1/20 hover:bg-white hover:text-color-1/40"
              >
                Clear
              </Button>
            </div>
          }
          disabled={disabledMatchers}
        />
      </PopoverContent>
    </Popover>
  )
}

function TrackModeHeader() {
  const {
    setMode: setMapMode,
    trackModeOptions,
    setTrackModeOptions,
  } = useMapStore((state) => state)
  const { startDate, endDate } = trackModeOptions

  const setStartDate = (date: Date | undefined) => {
    setTrackModeOptions({ ...trackModeOptions, startDate: date })
  }

  const setEndDate = (date: Date | undefined) => {
    setTrackModeOptions({ ...trackModeOptions, endDate: date })
  }

  const today = new Date();
  const minDate = startDate ? startDate : today;

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
        <div className="flex w-full items-center justify-center">
          <TrackModeDatePicker
            label="Start date"
            date={startDate}
            setDate={onSetStartDate}
            maxDate={today}
            className="flex-1"
          />
          <MinusIcon className="mx-2 size-4 text-color-1" />
          <TrackModeDatePicker
            label="End date"
            date={endDate}
            setDate={onSetEndDate}
            maxDate={today}
            minDate={minDate}
            className="flex-1"
          />
        </div>
      </div>
    </div>
  )
}

type TrackedVesselsPanelProps = {
  wideMode: boolean
}

export default function TrackedVesselsPanel({
  wideMode,
}: TrackedVesselsPanelProps) {
  const {
    trackedVesselIDs,
    mode: mapMode,
    setMode: setMapMode,
    trackModeOptions,
    setTrackModeOptions,
  } = useMapStore((state) => state)
  const { vessels: allVessels } = useVesselsStore((state) => state)
  const [trackedVesselsDetails, setTrackedVesselsDetails] = useState<Vessel[]>()

  useEffect(() => {
    const vesselsDetails = allVessels.filter((vessel) =>
      trackedVesselIDs.includes(vessel.id)
    )
    setTrackedVesselsDetails(vesselsDetails)
  }, [allVessels, trackedVesselIDs])

  const hasTrackedVessels = useMemo(() => {
    return trackedVesselIDs.length > 0
  }, [trackedVesselIDs])

  const onViewTracks = () => {
    setTrackModeOptions({
      ...trackModeOptions,
      vesselsIDsShown: trackedVesselIDs,
    })
    setMapMode("track")
  }

  const vesselsSelectedCount = trackedVesselIDs.length

  const [animateBadge, setAnimateBadge] = useState(false);

  useEffect(() => {
    if (vesselsSelectedCount > 0) {
      setAnimateBadge(true);
      const timer = setTimeout(() => setAnimateBadge(false), 300);
      return () => clearTimeout(timer);
    }
  }, [vesselsSelectedCount]);

  const WideModeTab = () => {
    return (
      <>
        {mapMode === "track" && <TrackModeHeader />}
        {!hasTrackedVessels && <NoVesselsPlaceholder />}

        {trackedVesselsDetails?.map((vessel: Vessel, index) => {
          return (
            <TrackedVesselItem
              key={vessel.id}
              vessel={vessel}
              colorIndex={index}
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
        >
          {!wideMode && (
            <div className="relative">
              <ShipIcon className="w-8 min-w-8" />
              {vesselsSelectedCount > 0 && (
                <Badge
                  variant="outline"
                  className={cn(
                    "absolute right-0 top-0 translate-x-1/2 -translate-y-1/2 flex justify-center items-center size-5 bg-color-1 text-color-3 border-none",
                    animateBadge && "animate-grow-shrink"
                  )}
                >
                  {vesselsSelectedCount}
                </Badge>
              )}
            </div>
          )}
          {mapMode === "position" && wideMode && (
            <span>{`Selected vessel (${trackedVesselIDs.length})`}</span>
          )}
        </h5>
      </div>

      {wideMode && <WideModeTab />}
    </>
  )
}
