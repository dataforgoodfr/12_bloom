"use client"

import { useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import type { PickingInfo } from "@deck.gl/core"
import { GeoJsonLayer } from "@deck.gl/layers"
import { SimpleMeshLayer } from "@deck.gl/mesh-layers"
import DeckGL from "@deck.gl/react"
import { registerLoaders } from "@loaders.gl/core"
import { OBJLoader } from "@loaders.gl/obj"
import { MapViewState, ScatterplotLayer } from "deck.gl"
import type { Feature, Geometry } from "geojson"
import { useTheme } from "next-themes"
import Map, { AttributionControl } from "react-map-gl/maplibre"

import { useMapStore } from "@/components/providers/map-store-provider"

const MESH_URL_LOCAL = `${process.env.NEXT_PUBLIC_VERCEL_URL ? process.env.NEXT_PUBLIC_VERCEL_URL : process.env.NEXT_PUBLIC_DOMAIN}/data/mesh/boat.obj`
const MESH_URL_REMOTE =
  "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/humanoid_quad.obj"

type VesselVoyageTracksPropertiesType = {
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

type ExamplePropertiesType = {
  name: string
  color: string
}

type BartStation = {
  name: string
  entries: number
  exits: number
  coordinates: [longitude: number, latitude: number]
}

const setPositionCoordinnates = (data: any) => {
  const longitude = data.position_longitude ? data.position_longitude : 0
  const latitude = data.position_latitude ? data.position_latitude : 0
  return [longitude, latitude, 0]
}

const latestPositions = new ScatterplotLayer<VesselPosition>({
  id: "vessels-latest-positions",
  data: `${process.env.NEXT_PUBLIC_VERCEL_URL ? process.env.NEXT_PUBLIC_VERCEL_URL : process.env.NEXT_PUBLIC_DOMAIN}/data/geometries/vessels_latest_positions.json`,
  getPosition: (d: VesselPosition) => [
    d.position_longitude,
    d.position_latitude,
  ],
  // data: "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart-stations.json",
  // getPosition: (d: BartStation) => d.coordinates,
  stroked: true,
  radiusUnits: "meters",
  getRadius: (d: VesselPosition) => d.vessel_length,
  radiusMinPixels: 3,
  radiusMaxPixels: 25,
  radiusScale: 200,
  getFillColor: [16, 181, 16, 210],
  getLineColor: [0, 0, 0],
  getLineWidth: 3,
  pickable: true,
})

const tracksByVesselAndVoyage =
  new GeoJsonLayer<VesselVoyageTracksPropertiesType>({
    id: "tracks_by_vessel_and_voyage",
    data: `${process.env.NEXT_PUBLIC_VERCEL_URL ? process.env.NEXT_PUBLIC_VERCEL_URL : process.env.NEXT_PUBLIC_DOMAIN}/data/geometries/all_tracks_by_vessel_and_voyage.geo.json`,
    getFillColor: [160, 160, 180, 200],
    getLineColor: [135, 24, 245, 200],
    pickable: true,
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

const mesh_layer = new SimpleMeshLayer({
  id: "vessels-latest-positions-mesh",
  // data: `${process.env.NEXT_PUBLIC_VERCEL_URL ? process.env.NEXT_PUBLIC_VERCEL_URL : process.env.NEXT_PUBLIC_DOMAIN}/geometries/latest_positions.json`,
  mesh: MESH_URL_LOCAL,
  // getPosition:  (d: Vessel) => [d.lng, d.lat, d.alt],
  // getPosition: (d) => [
  //   d.position_longitude ? d.position_longitude : 0,
  //   d.position_latitude ? d.position_latitude : 0,
  //   0,
  // ],
  // getColor: [255, 255, 255],
  // getOrientation: (d) => d.position_heading,
  data: "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart-stations.json",

  getColor: (d: BartStation) => [Math.sqrt(d.exits), 140, 0],
  getOrientation: (d: BartStation) => [0, Math.random() * 180, 0],
  getPosition: (d: BartStation) => d.coordinates,
  // mesh: "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/humanoid_quad.obj",
  sizeScale: 30,
  pickable: true,
  loaders: [OBJLoader],
})

export default function CoreMap() {
  const { setTheme, theme } = useTheme()
  useEffect(() => {
    setTheme("light")
  }, [setTheme])

  const { viewState, setViewState } = useMapStore((state) => state)

  const layers = [tracksByVesselAndVoyage, mesh_layer, latestPositions]
  console.log("layers", layers)

  return (
    <DeckGL
      viewState={viewState}
      controller={true}
      layers={layers}
      onViewStateChange={(e) => setViewState(e.viewState as MapViewState)}
      getTooltip={({ object }: PickingInfo<VesselPosition>) =>
        object
          ? `Name: ${object.vessel_name} | MMSI ${object.vessel_mmsi} | Length: ${object.vessel_length}`
          : null
      }
    >
      <Map
        mapStyle={`https://api.maptiler.com/maps/25f8f6d1-4c43-47ad-826a-14b40a83286f/style.json?key=${process.env.NEXT_PUBLIC_MAPTILER_TO}`}
        attributionControl={false}
      >
        {/* <AttributionControl
          style={{
            position: "fixed",
            bottom: "100%",
            width: "100%",
            zIndex: 20,
            color: "black",
          }}
          position="bottom-right"
        /> */}
      </Map>
    </DeckGL>
  )
}
