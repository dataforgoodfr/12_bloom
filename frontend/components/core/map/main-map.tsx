"use client"

import "maplibre-gl/dist/maplibre-gl.css"

import { useEffect, useMemo, useState } from "react"
import type { PickingInfo } from "@deck.gl/core"
import { GeoJsonLayer } from "@deck.gl/layers"
import DeckGL from "@deck.gl/react"
import chroma from "chroma-js"
import { IconLayer, Layer, MapViewState, PolygonLayer } from "deck.gl"
import { renderToString } from "react-dom/server"
import { Map as MapGL } from "react-map-gl/maplibre"

import {
  VesselExcursion,
  VesselExcursionSegment,
  VesselExcursionSegmentGeo,
  VesselExcursionSegments,
  VesselExcursionSegmentsGeo,
  VesselPosition,
  VesselPositions,
} from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import MapTooltip from "@/components/ui/tooltip-map-template"
import ZoneMapTooltip from "@/components/ui/zone-map-tooltip"
import { useMapStore } from "@/components/providers/map-store-provider"

type CoreMapProps = {
  vesselsPositions: VesselPositions
  zones: ZoneWithGeometry[]
  isLoading: {
    vessels: boolean
    positions: boolean
    zones: boolean
    excursions: boolean
  }
}

export default function CoreMap({
  vesselsPositions,
  zones,
  isLoading,
}: CoreMapProps) {
  const {
    viewState,
    setViewState,
    activePosition,
    setActivePosition,
    trackedVesselIDs,
    trackedVesselSegments,
    setLatestPositions,
    mode: mapMode,
    trackModeOptions,
  } = useMapStore((state) => state)

  // Use a piece of state that changes when `activePosition` changes to force re-render
  // const [layerKey, setLayerKey] = useState(0)

  const VESSEL_COLOR = [16, 181, 16, 210]
  const TRACKED_VESSEL_COLOR = [128, 16, 189, 210]

  function getColorFromValue(value: number): [number, number, number] {
    const scale = chroma.scale(["yellow", "red", "black"]).domain([0, 15])
    const color = scale(value).rgb()
    return [Math.round(color[0]), Math.round(color[1]), Math.round(color[2])]
  }

  const isVesselSelected = (vp: VesselPosition) => {
    return (
      vp.vessel.id === activePosition?.vessel.id ||
      trackedVesselIDs.includes(vp.vessel.id)
    )
  }

  function getTrackedVessels() {
    return trackedVesselIDs.map((id) => vesselsPositions.find((vp) => vp.vessel.id === id)).map((vp) => vp?.vessel)
  }

  useEffect(() => {
    setLatestPositions(vesselsPositions)
  }, [setLatestPositions, vesselsPositions])

  const onMapClick = ({ picked, object, layer }: PickingInfo) => {
    if (layer === null) {
      setActivePosition(null)
    }
  }

  const onVesselClick = ({ picked, object }: PickingInfo) => {
    setActivePosition(object as VesselPosition)
  }

  function toSegmentsGeo(segments: VesselExcursionSegment[] | undefined): VesselExcursionSegmentsGeo {
    if (!segments) return { type: "FeatureCollection", features: [] }
    const segmentsGeo = segments?.map((segment: VesselExcursionSegment) => {
      return {
        speed: segment.average_speed,
        navigational_status: "unknown",
        geometry: {
          type: "LineString",
          coordinates: [
            segment.start_position.coordinates,
            segment.end_position.coordinates,
          ],
        },
      }
    })
    return { type: "FeatureCollection", features: segmentsGeo ?? [] }
  }

  const latestPositions = new IconLayer<VesselPosition>({
    id: `vessels-latest-positions`,
    data: vesselsPositions,
    getPosition: (vp: VesselPosition) => [
      vp?.position?.coordinates[0],
      vp?.position?.coordinates[1],
    ],
    getAngle: (vp: VesselPosition) => (vp.heading ? Math.round(vp.heading) : 0),
    getIcon: () => "default",
    iconAtlas: "../../../img/map-vessel.png",
    iconMapping: {
      default: {
        x: 0,
        y: 0,
        width: 35,
        height: 27,
        mask: true,
      },
    },
    getSize: 16,
    getColor: (vp: VesselPosition) => {
      return new Uint8ClampedArray(
        isVesselSelected(vp) ? TRACKED_VESSEL_COLOR : VESSEL_COLOR
      )
    },
    pickable: true,
    onClick: onVesselClick,
    updateTriggers: {
      getColor: [activePosition?.vessel.id, trackedVesselIDs],
    },
  })

  const [segmentsLayer, setSegmentsLayer] = useState<Layer[]>([])

  function excursionToSegmentsLayer(excursion: VesselExcursion) {
    const segmentsGeo = toSegmentsGeo(excursion.segments)
    return new GeoJsonLayer<VesselExcursionSegmentGeo>({
      id: `${excursion.vessel_id}_vessel_trail`,
      data: segmentsGeo,
      getFillColor: (feature) => getColorFromValue(feature.properties?.speed),
      getLineColor: (feature) => getColorFromValue(feature.properties?.speed),
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

  useEffect(() => {
    console.log("mapMode", mapMode)
    if (mapMode === "track") {
      console.log("Map mode is track")
      const trackedVessels = getTrackedVessels();
      const layers: Layer[] = []

      console.log({trackedVessels})
      for (const vessel of trackedVessels) {
        const excursionsTimeframe = vessel?.excursions_timeframe;

        if (!excursionsTimeframe || !excursionsTimeframe.excursions || excursionsTimeframe.mapVisibility === false) {
          continue;
        }

        const excursions = excursionsTimeframe.excursions;
        console.log({excursions})
        for (const excursion of excursions) {
          if (excursion.mapVisibility === false) continue;

          layers.push(excursionToSegmentsLayer(excursion))  
        }
      }
      console.log("Layers", layers)
      setSegmentsLayer(layers)
    }
  }, [mapMode])

  const getObjectType = (
    object: VesselPosition | ZoneWithGeometry | undefined
  ) => {
    if (!object) return null
    return "vessel" in object ? "vessel" : "zone"
  }

  const zoneLayer = new PolygonLayer({
    id: `zones-layer`,
    data: zones,
    getPolygon: (d: ZoneWithGeometry) => {
      // Handle both Polygon and MultiPolygon types
      if (d.geometry.type === "MultiPolygon") {
        // Return the first polygon's coordinates for MultiPolygon
        return d.geometry.coordinates[0]
      }
      // For single Polygon, return just the first coordinate ring (outer boundary)
      return d.geometry.coordinates
    },
    getFillColor: (d: ZoneWithGeometry) => {
      switch (d.category) {
        case "territorial_seas":
          return [0, 0, 255, 50]
        case "fishing_coastal_waters":
          return [0, 255, 0, 50]
        case "amp":
        default:
          return [255, 0, 0, 50]
      }
    },
    getLineColor: [0, 0, 0, 128], // reduced opacity for borders
    getLineWidth: 1,
    lineWidthUnits: "pixels",
    lineWidthMinPixels: 1,
    pickable: true, // disable picking if not needed
    stroked: false,
    filled: true,
    wireframe: false, // disable wireframe for better performance
    extruded: false,
    parameters: {
      depthTest: false,
      blend: true,
      blendFunc: [770, 771], // standard transparency blending
    },
    onClick: () => {},
  })

  const layers = [
    // !isLoading.zones && zoneLayer,
    !isLoading.vessels && !isLoading.positions && !isLoading.excursions && segmentsLayer,
    !isLoading.positions && latestPositions,
  ].filter(Boolean) as Layer[]

  const getTooltip = ({
    object,
  }: Partial<PickingInfo<VesselPosition | ZoneWithGeometry>>) => {
    const objectType = getObjectType(object)
    const style = {
      backgroundColor: "#fff",
      fontSize: "0.8em",
      borderRadius: "10px",
      overflow: "hidden",
      padding: "0px",
    }
    let element: React.ReactNode
    if (objectType === "vessel") {
      const vesselInfo = object as VesselPosition
      element = <MapTooltip vesselInfo={vesselInfo} />
    } else if (objectType === "zone") {
      const zoneInfo = object as ZoneWithGeometry
      element = <ZoneMapTooltip zoneInfo={zoneInfo} />
    }
    return {
      html: renderToString(element),
      style,
    }
  }

  return (
    <DeckGL
      viewState={viewState}
      controller={true}
      layers={layers}
      onViewStateChange={(e) => setViewState(e.viewState as MapViewState)}
      getCursor={({ isHovering, isDragging }) => {
        return isDragging ? "move" : isHovering ? "pointer" : "grab"
      }}
      onClick={onMapClick}
      getTooltip={({
        object,
      }: PickingInfo<VesselPosition | ZoneWithGeometry>) => {
        if (!object) return null
        return getTooltip({ object })
      }}
    >
      <MapGL
        mapStyle={`https://api.maptiler.com/maps/e9b57486-1b91-47e1-a763-6df391697483/style.json?key=${process.env.NEXT_PUBLIC_MAPTILER_TO}`}
        attributionControl={false}
      ></MapGL>
    </DeckGL>
  )
}
