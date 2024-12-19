"use client"

import "maplibre-gl/dist/maplibre-gl.css"

import { useMemo } from "react"
import type { PickingInfo } from "@deck.gl/core"
import DeckGL from "@deck.gl/react"
import { Layer, MapViewState } from "deck.gl"
import { Map as MapGL } from "react-map-gl/maplibre"
import { useShallow } from "zustand/react/shallow"

import { Port } from "@/types/port"
import { ZoneWithGeometry } from "@/types/zone"
import { useMapStore } from "@/libs/stores/map-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"

import { useExcursionsLayers } from "./layers/use-excursions-layers"
import { usePortsLayers } from "./layers/use-ports-layers"
import { useVesselsLayers } from "./layers/use-vessels-layers"
import { useZonesLayer } from "./layers/use-zones-layer"
import { getPickObjectType } from "./utils"

type DeckGLMapProps = {
  zones: ZoneWithGeometry[]
  ports: Port[]
  onHover?: (info: PickingInfo) => void
}

export default function DeckGLMap({ zones, ports, onHover }: DeckGLMapProps) {
  const { setFocusedExcursionID } = useTrackModeOptionsStore(
    useShallow((state) => ({
      setFocusedExcursionID: state.setFocusedExcursionID,
    }))
  )

  const { viewState, setActivePosition, setViewState } = useMapStore(
    useShallow((state) => ({
      viewState: state.viewState,
      setViewState: state.setViewState,
      setActivePosition: state.setActivePosition,
    }))
  )

  const zonesLayer = useZonesLayer({ zones })
  const vesselsLayers = useVesselsLayers()
  const excursionsLayers = useExcursionsLayers()
  // const portsLayers = usePortsLayers()

  const onMapClick = (info: PickingInfo) => {
    const objectType = getPickObjectType(info)
    if (objectType !== "vessel" && objectType !== "excursion") {
      setActivePosition(null)
      setFocusedExcursionID(null)
    }
  }

  const onMapHover = (info: PickingInfo) => {
    onHover && onHover(info)
  }

  const layers = useMemo(
    () =>
      [zonesLayer, excursionsLayers, vesselsLayers]
        .flat()
        .filter(Boolean) as Layer[],
    [vesselsLayers, zonesLayer, excursionsLayers]
  )

  return (
    <DeckGL
      viewState={viewState}
      controller={{
        dragRotate: true,
        touchRotate: false,
        keyboard: false,
      }}
      layers={layers}
      onViewStateChange={(e) => setViewState(e.viewState as MapViewState)}
      getCursor={({ isHovering, isDragging }) => {
        return isDragging ? "move" : isHovering ? "pointer" : "grab"
      }}
      onHover={onMapHover}
      onClick={onMapClick}
    >
      <MapGL
        mapStyle={`https://api.maptiler.com/maps/e9b57486-1b91-47e1-a763-6df391697483/style.json?key=${process.env.NEXT_PUBLIC_MAPTILER_TO}`}
        attributionControl={false}
      ></MapGL>
    </DeckGL>
  )
}
