"use client"

import React, { useCallback, useEffect, useMemo, useState } from "react"
import type { PickingInfo } from "@deck.gl/core"
import { useShallow } from "zustand/react/shallow"

import { VesselPosition } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import { useTrackModeOptionsStore } from "@/libs/stores"
import { useMapStore } from "@/libs/stores/map-store"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import MapVesselTooltip from "@/components/ui/map-vessel-tooltip"
import MapZoneTooltip from "@/components/ui/map-zone-tooltip"

import DeckGLMap from "./deck-gl-map"
import PartnerCredits from "./partner-credits"
import { getPickObjectType } from "./utils"

type MainMapProps = {
  zones: ZoneWithGeometry[]
}

function CoordonatesIndicator({ coordinates }: { coordinates: string }) {
  return (
    <div className="absolute bottom-0 right-0 w-fit bg-color-3 px-4 py-2 text-xs text-color-4">
      {coordinates}
    </div>
  )
}

const MemoizedDeckGLMap = React.memo(DeckGLMap)

export default function MainMap({ zones }: MainMapProps) {
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
      const top = hoverInfo.y > -1 ? hoverInfo.y : screen.height / 2 - 110
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
    }

    return element
  }, [hoverInfo, activePosition])

  return (
    <div className="relative size-full">
      <PartnerCredits />
      <ContextMenu>
        <ContextMenuTrigger>
          <MemoizedDeckGLMap zones={zones} onHover={onMapHover} />
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
      <CoordonatesIndicator coordinates={coordinates} />
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
