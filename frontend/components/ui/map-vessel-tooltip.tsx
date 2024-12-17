import Image from "next/image"

import { VesselPosition } from "@/types/vessel"
import { Button } from "@/components/ui/button"
import Tooltip from "@/components/ui/custom/tooltip"

const getCountryISO2 = require("country-iso-3-to-2")

export interface MapVesselTooltipProps {
  top: number
  left: number
  vesselInfo: VesselPosition
  isSelected?: boolean
  isFrozen?: boolean
  onClose?: () => void
  onSelect?: () => void
}

const MapVesselTooltip = ({
  top,
  left,
  vesselInfo,
  isFrozen = false,
  onClose,
  isSelected = false,
  onSelect,
}: MapVesselTooltipProps) => {
  const {
    vessel: { mmsi, ship_name, imo, length, type, country_iso3 },
    timestamp,
  } = vesselInfo

  const formattedTimestamp = new Date(timestamp)
    .toLocaleString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZoneName: "short",
      timeZone: "UTC",
    })
    .replace(",", " -")

  return (
    <Tooltip
      top={top}
      left={left}
      width={288}
      isFrozen={isFrozen}
      onClose={onClose}
    >
      <div className="flex flex-col">
        <div className="relative">
          <Image
            className="rounded-t-lg"
            src="/img/scrombus.jpg"
            alt="default fishing vessel image"
            width={288}
            height={162}
          />
          <Image
            className="absolute bottom-[-11px] left-5 z-0 rounded-sm shadow-md"
            src={`https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/3.3.0/flags/4x3/${getCountryISO2(country_iso3)}.svg`.toLowerCase()}
            alt="country flag"
            width={40}
            height={40}
          />
        </div>
      </div>
      <div className="flex flex-col gap-8 rounded-b-lg bg-white p-5">
        <div className="flex flex-col">
          <h5 className="text-xl font-bold tracking-tight text-background dark:text-white">
            {ship_name}
          </h5>
          <p className="text-background">
            IMO {imo} / MMSI {mmsi}
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <div className="flex flex-col">
            <p className="text-background">
              <span className="font-bold">Type:</span> {type}
            </p>
            <p className="text-background">
              <span className="font-bold">Length:</span> {length} m
            </p>
          </div>
          <div className="flex flex-col">
            <p className="text-sm text-background">
              <span className="font-bold">Last position</span>
            </p>
            <p className="text-background">{formattedTimestamp}</p>
          </div>
          {onSelect && isFrozen && (
            <div className="flex flex-col">
              <Button
                onClick={onSelect}
                className={`hover:bg-none ${!isSelected ? "bg-color-1 hover:bg-color-1/50" : "bg-color-2 hover:bg-color-2/50"} w-32`}
              >
                {isSelected ? "Unselect" : "Select"} vessel
              </Button>
            </div>
          )}
        </div>
      </div>
    </Tooltip>
  )
}

export default MapVesselTooltip
