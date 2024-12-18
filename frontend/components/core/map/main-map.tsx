"use client"

import React, { useCallback, useEffect, useMemo, useState } from "react"
import type { PickingInfo } from "@deck.gl/core"
import { useShallow } from "zustand/react/shallow"

import { Port } from "@/types/port"
import { SegmentVesselPosition, VesselPosition } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import { useTrackModeOptionsStore } from "@/libs/stores"
import { useMapStore } from "@/libs/stores/map-store"
import { cn } from "@/libs/utils"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import MapPortTooltip from "@/components/ui/map-port-tooltip"
import MapVesselTooltip from "@/components/ui/map-vessel-tooltip"
import MapZoneTooltip from "@/components/ui/map-zone-tooltip"
import SegmentPositionTooltip from "@/components/ui/segment-position-tooltip"

import BottomRightCorner from "./bottom-right-corner"
import DeckGLMap from "./deck-gl-map"
import MapLegend from "./map-legend"
import PartnerCredits from "./partner-credits"
import { getPickObjectType } from "./utils"

type MainMapProps = {
  zones: ZoneWithGeometry[]
  ports: Port[]
}

function CoordonatesIndicator({
  coordinates,
  className,
}: {
  coordinates: string
  className: string
}) {
  return (
    <div
      className={cn(
        "w-fit bg-color-3 px-4 py-2 text-xs text-color-4",
        className
      )}
    >
      {coordinates}
    </div>
  )
}

const MemoizedDeckGLMap = React.memo(DeckGLMap)

export default function MainMap({ zones, ports }: MainMapProps) {
  const { activePosition, setActivePosition } = useMapStore(
    useShallow((state) => ({
      viewState: state.viewState,
      activePosition: state.activePosition,
      setActivePosition: state.setActivePosition,
    }))
  )

  const { addTrackedVessel, trackedVesselIDs, removeTrackedVessel } =
    useTrackModeOptionsStore(
      useShallow((state) => ({
        addTrackedVessel: state.addTrackedVessel,
        trackedVesselIDs: state.trackedVesselIDs,
        removeTrackedVessel: state.removeTrackedVessel,
      }))
    )

  const [tooltipPosition, setTooltipPosition] = useState<{
    top: number
    left: number
  } | null>(null)

  const [hoverInfo, setHoverInfo] = useState<PickingInfo | null>(null)
  const [previousCoordinates, setPreviousCoordinates] =
    useState<string>("-°N; -°E")

  const copyText = useCallback((text: string) => {
    navigator.clipboard.writeText(text)
  }, [])

  const isVesselTracked = (vesselId: number) => {
    return trackedVesselIDs.includes(vesselId)
  }

  const coordinates = useMemo(() => {
    if (!hoverInfo) return "-°N; -°E"
    const coordinate = hoverInfo.coordinate
    if (!coordinate) return previousCoordinates
    const latitude = coordinate[1].toFixed(3)
    const longitude = coordinate[0].toFixed(3)
    setPreviousCoordinates(`${latitude}°N; ${longitude}°E`)
    return `${latitude}°N; ${longitude}°E`
  }, [hoverInfo])

  useEffect(() => {
    if (activePosition && hoverInfo) {
      const top = hoverInfo.y > -1 ? hoverInfo.y : screen.height / 2 - 210
      const left = hoverInfo.x > -1 ? hoverInfo.x : screen.width / 2 + 10

      setTooltipPosition({
        top,
        left,
      })
    }
  }, [activePosition])

  const onMapHover = useCallback((hoverInfo: PickingInfo) => {
    setHoverInfo(hoverInfo)
  }, [])

  const onToggleTrackedVessel = (vesselId: number) => {
    if (trackedVesselIDs.includes(vesselId)) {
      removeTrackedVessel(vesselId)
    } else {
      addTrackedVessel(vesselId)
    }
  }

  const hoverTooltip = useMemo(() => {
    if (!hoverInfo) return

    const { object, x, y } = hoverInfo
    const objectType = getPickObjectType(hoverInfo)

    let element: React.ReactNode = null

    if (objectType === "vessel") {
      const vesselInfo = object as VesselPosition
      const vesselId = vesselInfo.vessel.id
      if (activePosition?.vessel.id !== vesselId) {
        element = <MapVesselTooltip vesselInfo={vesselInfo} top={y} left={x} />
      }
    } else if (objectType === "zone") {
      const zoneInfo = object as ZoneWithGeometry
      element = <MapZoneTooltip zoneInfo={zoneInfo} top={y} left={x} />
    } else if (objectType === "segmentPosition") {
      const segmentPositionInfo = object as SegmentVesselPosition
      element = (
        <SegmentPositionTooltip
          segmentPositionInfo={segmentPositionInfo}
          top={y}
          left={x}
        />
      )
    } else if (objectType === "port") {
      const portInfo = object as Port
      element = <MapPortTooltip portInfo={portInfo} top={y} left={x} />
    }

    return element
  }, [hoverInfo, activePosition])

  return (
    <div className="relative size-full">
      <PartnerCredits />
      <ContextMenu>
        <ContextMenuTrigger>
          <MemoizedDeckGLMap zones={zones} ports={ports} onHover={onMapHover} />
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem
            className="bg-background"
            onClick={() => copyText(coordinates)}
          >
            Copy coordinates
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>
      <BottomRightCorner coordinates={coordinates} />
      {tooltipPosition && activePosition && (
        <MapVesselTooltip
          top={tooltipPosition.top}
          left={tooltipPosition.left}
          vesselInfo={activePosition}
          isFrozen={true}
          isSelected={isVesselTracked(activePosition.vessel.id)}
          onClose={() => {
            setActivePosition(null)
          }}
          onSelect={() => {
            onToggleTrackedVessel(activePosition.vessel.id)
          }}
        />
      )}
      {hoverTooltip}
    </div>
  )
}
