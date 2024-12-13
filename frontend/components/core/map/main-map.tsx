"use client"

import { useCallback, useEffect, useState } from "react"
import type { PickingInfo } from "@deck.gl/core"

import { VesselPositions } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"

import DeckGLMap from "./deck-gl-map"
import React from "react"

type MainMapProps = {
  vesselsPositions: VesselPositions
  zones: ZoneWithGeometry[]
}

function CoordonatesIndicator({ coordinates }: { coordinates: string }) {
  return (
    <div className="absolute bottom-0 right-0 w-fit bg-color-3 px-4 py-2 text-xs text-color-4">
      {coordinates}
    </div>
  )
}

const MemoizedDeckGLMap = React.memo(DeckGLMap);

export default function MainMap({ vesselsPositions, zones }: MainMapProps) {
  const [coordinates, setCoordinates] = useState<string>("-°N; -°E")

  const onMapHover = useCallback(({ coordinate }: PickingInfo) => {
    coordinate &&
      setCoordinates(
        coordinate[1].toFixed(3).toString() +
          "°N; " +
          coordinate[0].toFixed(3) +
          "°E"
      )
  }, [])

  return (
    <div className="relative size-full">
      <MemoizedDeckGLMap
        vesselsPositions={vesselsPositions}
        zones={zones}
        onHover={onMapHover}
      />
      <CoordonatesIndicator coordinates={coordinates} />
    </div>
  )
}
