"use client";




import "maplibre-gl/dist/maplibre-gl.css";



import { useEffect, useMemo } from "react";
import type { PickingInfo } from "@deck.gl/core";
import { PathStyleExtension } from "@deck.gl/extensions";
import { GeoJsonLayer } from "@deck.gl/layers";
import DeckGL from "@deck.gl/react";
import chroma from "chroma-js";
import { IconLayer, Layer, MapViewState, PolygonLayer } from "deck.gl";
import { renderToString } from "react-dom/server";
import { Map as MapGL } from "react-map-gl/maplibre";



import { VesselExcursionSegment, VesselExcursionSegmentGeo, VesselExcursionSegments, VesselExcursionSegmentsGeo, VesselPosition, VesselPositions } from "@/types/vessel";
import { ZoneCategory, ZoneWithGeometry } from "@/types/zone";
import MapTooltip from "@/components/ui/tooltip-map-template";
import ZoneMapTooltip from "@/components/ui/zone-map-tooltip";
import { useMapStore } from "@/components/providers/map-store-provider";





type CoreMapProps = {
  vesselsPositions: VesselPositions
  zones: ZoneWithGeometry[]
  isLoading: {
    vessels: boolean
    positions: boolean
    zones: boolean
  }
}

const VESSEL_COLOR = [16, 181, 16, 0]
const TRACKED_VESSEL_COLOR = [255, 255, 255]

// Add a type to distinguish zones
type ZoneWithType = ZoneWithGeometry & {
  renderType: "amp" | "territorial" | "fishing"
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
  } = useMapStore((state) => state)

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

  // useEffect(() => {
  //   // This will change the key of the layer, forcing it to re-render when `activePosition` changes
  //   setLayerKey((prevKey) => prevKey + 1)
  // }, [activePosition, trackedVesselIDs])

  useEffect(() => {
    setLatestPositions(vesselsPositions)
  }, [setLatestPositions, vesselsPositions])

  const onMapClick = ({ layer }: PickingInfo) => {
    if (layer?.id !== "vessels-latest-positions") {
      setActivePosition(null)
    }
  }

  const onVesselClick = ({ object }: PickingInfo) => {
    setActivePosition(object as VesselPosition)
  }

  const onZoneClick = () => {
    return
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

  const tracksByVesselAndVoyage = trackedVesselSegments
    .map((segments) => toSegmentsGeo(segments))
    .map((segmentsGeo: VesselExcursionSegmentsGeo) => {
      return new GeoJsonLayer<VesselExcursionSegmentGeo>({
        id: `${segmentsGeo.vesselId}_vessel_trail`,
        data: segmentsGeo,
        getFillColor: (feature) => getColorFromValue(feature.properties?.speed),
        // getLineColor: (feature) => getColorFromValue(feature.properties?.speed),
        getLineColor: [255, 255, 255],
        pickable: false,
        stroked: true,
        filled: false,
        getLineWidth: 1,
        lineWidthMinPixels: 0.5,
        lineWidthMaxPixels: 3,
        lineWidthUnits: "pixels",
        lineWidthScale: 2,
        getPointRadius: 4,
        getTextSize: 12,
      })
    })

  const getObjectType = (
    object: VesselPosition | ZoneWithGeometry | undefined
  ) => {
    if (!object) return null
    return "vessel" in object ? "vessel" : "zone"
  }

  // Single combined layer instead of three separate ones
  const combinedZonesLayer = useMemo(
    () =>
      new PolygonLayer({
        id: "combined-zones-layer",
        data: zones,
        getPolygon: (d: ZoneWithType) => {
          if (d.geometry.type === "MultiPolygon") {
            return d.geometry.coordinates[0]
          }
          return d.geometry.coordinates
        },
        getFillColor: (d: ZoneWithType) => {
          switch (d.category) {
            case ZoneCategory.AMP:
              return [30, 224, 171, 25]
            case ZoneCategory.FISHING_COASTAL_WATERS:
              return [132, 0, 0, 25]
            case ZoneCategory.TERRITORIAL_SEAS:
            default:
              return [0, 0, 0, 0]
          }
        },
        getLineColor: (d: ZoneWithType) => {
          switch (d.category) {
            case ZoneCategory.AMP:
              return [44, 226, 176, 255]
            case ZoneCategory.TERRITORIAL_SEAS:
              return [132, 0, 0, 255]
            case ZoneCategory.FISHING_COASTAL_WATERS:
            default:
              return [0, 0, 0, 0]
          }
        },
        getLineWidth: (d: ZoneWithType) =>
          d.category !== ZoneCategory.FISHING_COASTAL_WATERS ? 0.5 : 0,
        lineWidthUnits: "pixels",
        pickable: true,
        stroked: true,
        filled: true,
        wireframe: false,
        extruded: false,
        // Only apply dash pattern to AMP zones
        // getDashArray: [4, 12],
        extensions: zones.some((z) => z.category === ZoneCategory.AMP)
          ? [new PathStyleExtension({ dash: true })]
          : [],
        parameters: {
          depthTest: false,
          blendFunc: [770, 771], // standard transparency blending
        },
        onClick: onZoneClick,
      }),
    [zones]
  )

  const layers = [
    !isLoading.zones && combinedZonesLayer,
    !isLoading.vessels && !isLoading.positions && tracksByVesselAndVoyage,
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
function toSegmentsGeo({ segments, vesselId }: VesselExcursionSegments): any {
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
  return { vesselId, type: "FeatureCollection", features: segmentsGeo ?? [] }
}