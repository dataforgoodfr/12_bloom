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
import { ZoneCategory, ZoneWithGeometry } from "@/types/zone"
import MapTooltip from "@/components/ui/tooltip-map-template"
import ZoneMapTooltip from "@/components/ui/zone-map-tooltip"

import { useMapStore } from "@/libs/stores/map-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { useShallow } from "zustand/react/shallow"

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

const VESSEL_COLOR = [16, 181, 16, 210]
const TRACKED_VESSEL_COLOR = [128, 16, 189, 210]

// Add a type to distinguish zones
type ZoneWithType = ZoneWithGeometry & {
  renderType: "amp" | "territorial" | "fishing"
}

export default function CoreMap({
  vesselsPositions,
  zones,
  isLoading,
}: CoreMapProps) {
  const { trackedVesselIDs } = useTrackModeOptionsStore(
    useShallow((state) => ({
      trackedVesselIDs: state.trackedVesselIDs,
    }))
  )

  const {
    mode: mapMode,
    viewState,
    activePosition,
    displayedZones,
    setActivePosition,
    setViewState,
  } = useMapStore(useShallow((state) => ({
    mode: state.mode,
    viewState: state.viewState,
    activePosition: state.activePosition,
    displayedZones: state.displayedZones,
    setViewState: state.setViewState,
    setActivePosition: state.setActivePosition,
    }))
  )

  const [coordinates, setCoordinates] = useState<string>("-°N -°E")

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

  const onMapClick = ({ layer }: PickingInfo) => {
    if (layer?.id !== "vessels-latest-positions") {
      setActivePosition(null)
    }
  }

  const onVesselClick = ({ object }: PickingInfo) => {
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

  const latestPositions = useMemo(
    () =>
      new IconLayer<VesselPosition>({
        id: `vessels-latest-positions`,
        data: vesselsPositions,
        getPosition: (vp: VesselPosition) => [
          vp?.position?.coordinates[0],
          vp?.position?.coordinates[1],
        ],
        getAngle: (vp: VesselPosition) =>
          vp.heading ? Math.round(vp.heading) : 0,
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
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      vesselsPositions,
      activePosition?.vessel.id,
      trackedVesselIDs,
      isVesselSelected,
    ]
  )

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
    if (mapMode === "track") {
      const trackedVessels = getTrackedVessels();
      const layers: Layer[] = []

      for (const vessel of trackedVessels) {
        const excursionsTimeframe = vessel?.excursions_timeframe;

        if (!excursionsTimeframe || !excursionsTimeframe.excursions || excursionsTimeframe.mapVisibility === false) {
          continue;
        }

        const excursions = excursionsTimeframe.excursions;
        for (const excursion of excursions) {
          if (excursion.mapVisibility === false) continue;

          layers.push(excursionToSegmentsLayer(excursion))
        }
      }
      console.log("Layers", layers)
      setSegmentsLayer(layers)
    }
  }, [mapMode])

  const onMapHover = ({ coordinate }: PickingInfo) => {
    coordinate &&
      setCoordinates(
        coordinate[1].toFixed(3).toString() +
          "°N " +
          coordinate[0].toFixed(3) +
          "°E"
      )
  }

  const getObjectType = (
    object: VesselPosition | ZoneWithGeometry | undefined
  ) => {
    if (!object) return null
    return "vessel" in object ? "vessel" : "zone"
  }

  const isAMPDisplayed = displayedZones.includes(ZoneCategory.AMP)
  const isTerritorialDisplayed = displayedZones.includes(
    ZoneCategory.TERRITORIAL_SEAS
  )
  const isFishingDisplayed = displayedZones.includes(
    ZoneCategory.FISHING_COASTAL_WATERS
  )

  const ampMultiZones = useMemo(() => {
    const filteredZones = isAMPDisplayed
      ? zones
          .filter((z) => z.category === ZoneCategory.AMP)
          .filter((z) => z.geometry.type === "MultiPolygon")
      : []
    return filteredZones
  }, [isAMPDisplayed, zones])

  const ampSingleZones = useMemo(() => {
    const filteredZones = isAMPDisplayed
      ? zones
          .filter((z) => z.category === ZoneCategory.AMP)
          .filter((z) => z.geometry.type === "Polygon")
      : []
    return filteredZones
  }, [isAMPDisplayed, zones])

  const territorialZones = useMemo(
    () =>
      isTerritorialDisplayed
        ? zones.filter((z) => z.category === ZoneCategory.TERRITORIAL_SEAS)
        : [],
    [isTerritorialDisplayed, zones]
  )
  const fishingZones = useMemo(
    () =>
      isFishingDisplayed
        ? zones.filter(
            (z) => z.category === ZoneCategory.FISHING_COASTAL_WATERS
          )
        : [],
    [isFishingDisplayed, zones]
  )

  const ampMultiZonesLayer = useMemo(
    () =>
      new GeoJsonLayer<ZoneWithGeometry>({
        id: "amp-zones-layer",
        data: {
          type: "FeatureCollection",
          features: ampMultiZones.map((zone) => ({
            type: "Feature",
            properties: {
              name: zone.name,
            },
            geometry: {
              type: "MultiPolygon",
              coordinates: zone.geometry.coordinates,
            },
          })),
        },
        getFillColor: [30, 224, 171, 25],
        pickable: true,
        stroked: false,
        filled: true,
        wireframe: false,
        extruded: false,
        visible: isAMPDisplayed,
      }),
    [ampMultiZones, isAMPDisplayed]
  )

  const ampSingleZonesLayer = useMemo(
    () =>
      new PolygonLayer({
        id: "amp-single-zones-layer",
        data: ampSingleZones,
        getPolygon: (d) => d.geometry.coordinates,
        getFillColor: [30, 224, 171, 25],
        pickable: true,
        stroked: false,
        filled: true,
        wireframe: false,
        extruded: false,
        parameters: {
          depthTest: false,
          blendFunc: [770, 771],
        },
        visible: isAMPDisplayed,
      }),
    [ampSingleZones, isAMPDisplayed]
  )

  const territorialZonesLayer = useMemo(
    () =>
      new PolygonLayer({
        id: "territorial-zones-layer",
        data: territorialZones,
        getPolygon: (d) => {
          return d.geometry.type === "MultiPolygon"
            ? d.geometry.coordinates[0]
            : d.geometry.coordinates
        },
        getFillColor: [0, 0, 0, 0],
        getLineColor: [132, 0, 0, 255],
        getLineWidth: 0.5,
        lineWidthUnits: "pixels",
        pickable: true,
        stroked: true,
        filled: true,
        wireframe: false,
        extruded: false,
        parameters: {
          depthTest: false,
          blendFunc: [770, 771],
        },
        visible: isTerritorialDisplayed,
      }),
    [territorialZones, isTerritorialDisplayed]
  )

  const fishingZonesLayer = useMemo(
    () =>
      new PolygonLayer({
        id: "fishing-zones-layer",
        data: fishingZones,
        getPolygon: (d) => {
          return d.geometry.type === "MultiPolygon"
            ? d.geometry.coordinates[0]
            : d.geometry.coordinates
        },
        getFillColor: [132, 0, 0, 25],
        getLineColor: [0, 0, 0, 0],
        getLineWidth: 0,
        lineWidthUnits: "pixels",
        pickable: true,
        stroked: false,
        filled: true,
        wireframe: false,
        extruded: false,
        parameters: {
          depthTest: false,
          blendFunc: [770, 771],
        },
        visible: isFishingDisplayed,
      }),
    [fishingZones, isFishingDisplayed]
  )

  const layers = useMemo(
    () =>
      [
        !isLoading.zones && [
          ampMultiZonesLayer,
          ampSingleZonesLayer,
          territorialZonesLayer,
          fishingZonesLayer,
        ],
        !isLoading.vessels && !isLoading.positions && segmentsLayer,
        !isLoading.positions && latestPositions,
      ]
        .flat()
        .filter(Boolean) as Layer[],
    [
      isLoading.zones,
      isLoading.vessels,
      isLoading.positions,
      ampMultiZonesLayer,
      ampSingleZonesLayer,
      territorialZonesLayer,
      fishingZonesLayer,
      segmentsLayer,
      latestPositions,
    ]
  )

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
      onHover={onMapHover}
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
      <div className="absolute bottom-0 right-0 w-fit bg-color-3 px-4 py-2 text-xs text-color-4">
        {coordinates}
      </div>
    </DeckGL>
  )
}
