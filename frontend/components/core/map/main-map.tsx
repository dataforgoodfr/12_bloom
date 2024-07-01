"use client"

import "maplibre-gl/dist/maplibre-gl.css"

import { useEffect, useState } from "react"
import type { PickingInfo } from "@deck.gl/core"
import { GeoJsonLayer } from "@deck.gl/layers"
import { SimpleMeshLayer } from "@deck.gl/mesh-layers"
import DeckGL from "@deck.gl/react"
import { OBJLoader } from "@loaders.gl/obj"
import chroma from "chroma-js"
import { FlyToInterpolator, MapViewState, ScatterplotLayer } from "deck.gl"
import { useTheme } from "next-themes"
import { renderToString } from "react-dom/server"
import Map from "react-map-gl/maplibre"

import MapTooltip from "@/components/ui/tooltip-map-template"
import { useMapStore } from "@/components/providers/map-store-provider"
import { VesselPosition, VesselPositions, VesselTrailPropertiesType } from "@/types/vessel"

const MESH_URL_LOCAL = `../../../data/mesh/boat.obj`

type BartStation = {
  name: string
  entries: number
  exits: number
  coordinates: [longitude: number, latitude: number]
}

type CoreMapProps = {
  vesselsPositions: VesselPositions;
}

export default function CoreMap({ vesselsPositions }: CoreMapProps) {
  const { setTheme, theme } = useTheme()

  const {
    viewState,
    setViewState,
    activePosition,
    setActivePosition,
    trackedVesselMMSIs,
    setLatestPositions,
  } = useMapStore((state) => state)

  // Use a piece of state that changes when `activePosition` changes to force re-render
  const [layerKey, setLayerKey] = useState(0)

  function getColorFromValue(value: number): [number, number, number] {
    const scale = chroma.scale(["yellow", "red", "black"]).domain([0, 15])
    const color = scale(value).rgb()
    return [Math.round(color[0]), Math.round(color[1]), Math.round(color[2])]
  }

  useEffect(() => {
    // This will change the key of the layer, forcing it to re-render when `activePosition` changes
    setLayerKey((prevKey) => prevKey + 1)
  }, [activePosition, trackedVesselMMSIs])

  useEffect(() => {
    setLatestPositions(vesselsPositions);
  }, [vesselsPositions])

  const latestPositions = new ScatterplotLayer<VesselPosition>({
    id: `vessels-latest-positions-${layerKey}`,
    data: vesselsPositions,
    getPosition: (vp: VesselPosition) => [
      vp?.position?.coordinates[0],
      vp?.position?.coordinates[1],
    ],
    stroked: true,
    radiusUnits: "meters",
    getRadius: (vp: VesselPosition) => vp.vessel.length,
    radiusMinPixels: 3,
    radiusMaxPixels: 25,
    radiusScale: 200,
    getFillColor: (vp: VesselPosition) => {
      return vp.vessel.mmsi === activePosition?.vessel.mmsi ||
        trackedVesselMMSIs.includes(vp.vessel.mmsi)
        ? [128, 16, 189, 210]
        : [16, 181, 16, 210]
    },
    getLineColor: [0, 0, 0],
    getLineWidth: 3,
    pickable: true,
    onClick: ({ object }) => {
      setActivePosition(object as VesselPosition)
      setViewState({
        ...viewState,
        longitude: object?.position?.coordinates[0],
        latitude: object?.position?.coordinates[1],
        zoom: 7,
        pitch: 40,
        transitionInterpolator: new FlyToInterpolator({ speed: 2 }),
        transitionDuration: "auto",
      })
    },
  })

  // TODO(CT): call backend
  const tracksByVesselAndVoyage = trackedVesselMMSIs.map(
    (trackedVesselMMSI) => {
      return new GeoJsonLayer<VesselTrailPropertiesType>({
        id: `${trackedVesselMMSI}_vessel_trail_${layerKey}`,
        data: `../../../data/geometries/segments_by_vessel_mmsi/${trackedVesselMMSI}_segments.geo.json`,
        getFillColor: ({ properties }) => getColorFromValue(properties.speed),
        getLineColor: ({ properties }) => {
          return getColorFromValue(properties.speed)
        },
        pickable: false,
        stroked: false,
        filled: true,
        getLineWidth: 1,
        lineWidthMinPixels: 0.5,
        lineWidthMaxPixels: 3,
        lineWidthUnits: "pixels",
        lineWidthScale: 2,
        getPointRadius: 4,
        getTextSize: 12,
      })
    }
  )

  const positions_mesh_layer = new SimpleMeshLayer({
    id: `vessels-positions-mesh-layer-${layerKey}`,
    data: vesselsPositions,
    mesh: MESH_URL_LOCAL,
    getPosition: (vp: VesselPosition) => [
      vp?.position?.coordinates[0],
      vp?.position?.coordinates[1],
    ],
    getColor: (vp: VesselPosition) => {
      return vp.vessel.mmsi === activePosition?.vessel.mmsi ||
        trackedVesselMMSIs.includes(vp.vessel.mmsi)
        ? [128, 16, 189, 210]
        : [16, 181, 16, 210]
    },
    getOrientation: (vp: VesselPosition) => [
      0,
      Math.round(vp.heading ? vp.heading : 0),
      90,
    ],
    getScale: (vp: VesselPosition) => [
      vp.vessel.length,
      vp.vessel.length * 1.5,
      vp.vessel.length / 1.5,
    ],
    scaleUnits: "pixels",
    sizeScale: 100,
    pickable: true,
    onClick: ({ object }) => {
      setActivePosition(object as VesselPosition)
      setViewState({
        ...viewState,
        longitude: object?.position?.coordinates[0],
        latitude: object?.position?.coordinates[1],
        zoom: 10,
        transitionInterpolator: new FlyToInterpolator({ speed: 2 }),
        transitionDuration: "auto",
      })
    },
    loaders: [OBJLoader],
  })

  const layers = [
    tracksByVesselAndVoyage,
    latestPositions,
    positions_mesh_layer,
  ]

  useEffect(() => {
    setTheme("light")
  }, [setTheme])

  return (
    <DeckGL
      viewState={viewState}
      controller={true}
      layers={layers}
      onViewStateChange={(e) => setViewState(e.viewState as MapViewState)}
      getTooltip={({ object }: PickingInfo<VesselPosition>) =>
        object
          ? {
              html: renderToString(<MapTooltip vesselInfo={object} />),
              style: {
                backgroundColor: "#fff",
                fontSize: "0.8em",
                borderRadius: "10px",
                overflow: "hidden",
                padding: "0px",
              },
            }
          : null
      }
    >
      <Map
        mapStyle={`https://api.maptiler.com/maps/bb513c96-848e-4775-b150-437395193f26/style.json?key=${process.env.NEXT_PUBLIC_MAPTILER_TO}`}
        attributionControl={false}
      ></Map>
    </DeckGL>
  )
}
