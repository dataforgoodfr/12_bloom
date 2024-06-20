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

const MESH_URL_LOCAL = `../../../data/mesh/boat.obj`

export type VesselVoyageTracksPropertiesType = {
  vessel_ais_class: string
  vessel_flag: string
  vessel_name: string
  vessel_callsign: string
  vessel_ship_type?: string
  vessel_sub_ship_type?: string
  vessel_mmsi: number
  vessel_imo: number
  vessel_width: number
  vessel_length: number
  voyage_destination?: string
  voyage_draught?: number
  voyage_eta: string
}

export type VesselTrailPropertiesType = {
  vessel_mmsi: number
  speed: number
  heading?: number
  navigational_status: string
}

export type VesselPositions = VesselPosition[]

export interface VesselPosition {
  vessel_flag: string
  vessel_name: string
  vessel_callsign: string
  vessel_ship_type?: string
  vessel_mmsi: number
  vessel_imo: number
  vessel_width: number
  vessel_length: number
  position_accuracy: string
  position_collection_type: string
  position_course: number
  position_heading?: number
  position_latitude: number
  position_longitude: number
  position_navigational_status: string
  position_speed: number
  position_timestamp: string
  voyage_destination?: string
  voyage_draught?: number
}

type BartStation = {
  name: string
  entries: number
  exits: number
  coordinates: [longitude: number, latitude: number]
}

export default function CoreMap() {
  const { setTheme, theme } = useTheme()

  const {
    viewState,
    setViewState,
    activePosition,
    setActivePosition,
    trackedVesselMMSIs,
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

  const latestPositions = new ScatterplotLayer<VesselPosition>({
    id: `vessels-latest-positions-${layerKey}`,
    data: `../../../data/geometries/vessels_latest_positions.json`,
    getPosition: (d: VesselPosition) => [
      d.position_longitude,
      d.position_latitude,
    ],
    stroked: true,
    radiusUnits: "meters",
    getRadius: (d: VesselPosition) => d.vessel_length,
    radiusMinPixels: 3,
    radiusMaxPixels: 25,
    radiusScale: 200,
    getFillColor: (d: VesselPosition) => {
      return d.vessel_mmsi === activePosition?.vessel_mmsi ||
        trackedVesselMMSIs.includes(d.vessel_mmsi)
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
        longitude: object.position_longitude,
        latitude: object.position_latitude,
        zoom: 7,
        pitch: 40,
        transitionInterpolator: new FlyToInterpolator({ speed: 2 }),
        transitionDuration: "auto",
      })
    },
  })

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
    data: `../../../data/geometries/vessels_latest_positions.json`,
    mesh: MESH_URL_LOCAL,
    getPosition: (d: VesselPosition) => [
      d.position_longitude,
      d.position_latitude,
    ],
    getColor: (d: VesselPosition) => {
      return d.vessel_mmsi === activePosition?.vessel_mmsi ||
        trackedVesselMMSIs.includes(d.vessel_mmsi)
        ? [128, 16, 189, 210]
        : [16, 181, 16, 210]
    },
    getOrientation: (d: VesselPosition) => [
      0,
      Math.round(d.position_heading ? d.position_heading : 0),
      90,
    ],
    getScale: (d: VesselPosition) => [
      d.vessel_length,
      d.vessel_length * 1.5,
      d.vessel_length / 1.5,
    ],
    scaleUnits: "pixels",
    sizeScale: 100,
    pickable: true,
    onClick: ({ object }) => {
      setActivePosition(object as VesselPosition)
      setViewState({
        ...viewState,
        longitude: object.position_longitude,
        latitude: object.position_latitude,
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
