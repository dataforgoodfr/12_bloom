"use client"

import { useEffect, useMemo, useState } from "react"
import { PopoverContent, PopoverTrigger } from "@radix-ui/react-popover"
import { format } from "date-fns"
import {
  ChevronRight,
  MinusIcon,
  PenIcon,
  Ship as ShipIcon,
  XIcon,
} from "lucide-react"
import { DayPicker, getDefaultClassNames, Matcher } from "react-day-picker"
import { useShallow } from "zustand/react/shallow"

import { Vessel } from "@/types/vessel"
import { useMapStore } from "@/libs/stores/map-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { useVesselsStore } from "@/libs/stores/vessels-store"
import { cn } from "@/libs/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Popover } from "@/components/ui/popover"

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
    <div className="flex justify-center gap-4">
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
        Show tracks
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
            "justify-center bg-white text-center font-normal !text-color-2 shadow-md hover:border-color-1 hover:bg-white",
            !date && "text-muted-foreground",
            className
          )}
          color="primary"
        >
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
  const { setMode: setMapMode } = useMapStore(
    useShallow((state) => ({
      setMode: state.setMode,
    }))
  )

  const { startDate, endDate, setStartDate, setEndDate } =
    useTrackModeOptionsStore(
      useShallow((state) => ({
        startDate: state.startDate,
        endDate: state.endDate,
        setStartDate: state.setStartDate,
        setEndDate: state.setEndDate,
      }))
    )

  const [startDateSelected, setStartDateSelected] = useState(startDate)
  const [endDateSelected, setEndDateSelected] = useState(endDate)

  const today = new Date()
  const minDate = startDate ? startDate : today

  const onSetStartDate = (date: Date | undefined) => {
    setStartDateSelected(date)
    if (date && endDateSelected && date > endDateSelected) {
      setEndDateSelected(undefined)
    }
  }

  const onSetEndDate = (date: Date | undefined) => {
    setEndDateSelected(date)
  }

  const onApply = () => {
    setStartDate(startDateSelected)
    setEndDate(endDateSelected)
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
        <div className="flex w-full items-center justify-center gap-2">
          <TrackModeDatePicker
            label="Start date"
            date={startDateSelected}
            setDate={onSetStartDate}
            maxDate={today}
            className="flex-1"
          />
          <MinusIcon className="size-4 text-color-1" />
          <TrackModeDatePicker
            label="End date"
            date={endDateSelected}
            setDate={onSetEndDate}
            maxDate={today}
            minDate={minDate}
            className="flex-1"
          />
          <Button onClick={onApply}>OK</Button>
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
    mode: mapMode,
    setMode: setMapMode,
    setActivePosition: setActivePosition,
  } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      setMode: state.setMode,
      setActivePosition: state.setActivePosition,
    }))
  )

  const { trackedVesselIDs, setTrackedVesselIDs } = useTrackModeOptionsStore(
    useShallow((state) => ({
      trackedVesselIDs: state.trackedVesselIDs,
      setTrackedVesselIDs: state.setTrackedVesselIDs,
    }))
  )

  const { vessels: allVessels } = useVesselsStore(
    useShallow((state) => ({
      vessels: state.vessels,
    }))
  )

  const trackedVesselsDetails = useMemo(() => {
    return allVessels.filter((vessel) => trackedVesselIDs.includes(vessel.id))
  }, [allVessels, trackedVesselIDs])

  const hasTrackedVessels = useMemo(() => {
    return trackedVesselIDs.length > 0
  }, [trackedVesselIDs])

  const onViewTracks = () => {
    setMapMode("track")
    setActivePosition(null)
  }

  const vesselsSelectedCount = trackedVesselIDs.length

  const [animateBadge, setAnimateBadge] = useState(false)

  useEffect(() => {
    if (vesselsSelectedCount > 0) {
      setAnimateBadge(true)
      const timer = setTimeout(() => setAnimateBadge(false), 300)
      return () => clearTimeout(timer)
    }
  }, [vesselsSelectedCount])

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
              listIndex={index}
              className={`${
                index < trackedVesselsDetails.length - 1
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
      <div className="flex items-center justify-center text-sm font-bold uppercase">
        {!wideMode && (
          <div className="relative flex size-8 items-center justify-center">
            <ShipIcon
              className="size-8 text-neutral-200 hover:text-primary"
              strokeWidth={1}
            />
            {vesselsSelectedCount > 0 && (
              <Badge
                variant="outline"
                className={cn(
                  "absolute right-0 top-0 flex size-5 -translate-y-1/2 translate-x-1/2 items-center justify-center border-none bg-color-1 text-color-3",
                  animateBadge && "animate-grow-shrink"
                )}
              >
                {vesselsSelectedCount}
              </Badge>
            )}
          </div>
        )}
        {mapMode === "position" && wideMode && (
          <div className="flex w-full items-center justify-start gap-3">
            <ShipIcon className="size-8 text-neutral-200" strokeWidth={1} />
            <span className="text-start text-card">{`Selected vessels (${trackedVesselIDs.length})`}</span>
          </div>
        )}
      </div>

      {wideMode && <WideModeTab />}
    </>
  )
}
