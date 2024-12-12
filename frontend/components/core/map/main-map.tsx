"use client";




import "maplibre-gl/dist/maplibre-gl.css";



import { useEffect, useMemo, useState } from "react";
import type { PickingInfo } from "@deck.gl/core";
import { GeoJsonLayer } from "@deck.gl/layers";
import DeckGL from "@deck.gl/react";
import chroma from "chroma-js";
import { IconLayer, Layer, MapViewState, PolygonLayer } from "deck.gl";
import type { Feature, Geometry } from "geojson";
import { renderToString } from "react-dom/server";
import { Map as MapGL } from "react-map-gl/maplibre";
import { useShallow } from "zustand/react/shallow";



import { VesselExcursion, VesselExcursionSegment, VesselExcursionSegmentGeo, VesselExcursionSegmentsGeo, VesselPosition, VesselPositions } from "@/types/vessel";
import { ZoneCategory, ZoneWithGeometry } from "@/types/zone";
import { getVesselColorRGB } from "@/libs/colors";
import { useLoaderStore } from "@/libs/stores/loader-store";
import { useMapStore } from "@/libs/stores/map-store";
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store";
import MapTooltip from "@/components/ui/tooltip-map-template";
import ZoneMapTooltip from "@/components/ui/zone-map-tooltip";





type CoreMapProps = {
  vesselsPositions: VesselPositions
  zones: ZoneWithGeometry[]
}

// Add a type to distinguish zones
type ZoneWithType = ZoneWithGeometry & {
  renderType: "amp" | "territorial" | "fishing"
}

const getOpacityFromTimestamp = (timestamp: string) => {
  const now = new Date()
  const positionTime = new Date(timestamp)
  const diffInHours =
    (now.getTime() - positionTime.getTime()) / (1000 * 60 * 60)

  if (diffInHours <= 0.75) return 255 // 100% opacity
  if (diffInHours <= 3) return 255 // 70% opacity
  if (diffInHours <= 5) return 255 // 55% opacity
  return 255 // 40% opacity
}

export default function CoreMap({ vesselsPositions, zones }: CoreMapProps) {
  const {
    trackedVesselIDs,
    vesselsIDsHidden,
    excursions,
    excursionsIDsHidden,
    focusedExcursionID,
    setFocusedExcursionID,
  } = useTrackModeOptionsStore(
    useShallow((state) => ({
      trackedVesselIDs: state.trackedVesselIDs,
      vesselsIDsHidden: state.vesselsIDsHidden,
      excursionsIDsHidden: state.excursionsIDsHidden,
      excursions: state.excursions,
      focusedExcursionID: state.focusedExcursionID,
      setFocusedExcursionID: state.setFocusedExcursionID,
    }))
  )

  const {
    mode: mapMode,
    viewState,
    activePosition,
    displayedZones,
    setActivePosition,
    setViewState,
    setLeftPanelOpened,
  } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      viewState: state.viewState,
      activePosition: state.activePosition,
      displayedZones: state.displayedZones,
      setViewState: state.setViewState,
      setActivePosition: state.setActivePosition,
      setLeftPanelOpened: state.setLeftPanelOpened,
    }))
  )

  const { zonesLoading, positionsLoading, vesselsLoading, excursionsLoading } =
    useLoaderStore(
      useShallow((state) => ({
        zonesLoading: state.zonesLoading,
        positionsLoading: state.positionsLoading,
        vesselsLoading: state.vesselsLoading,
        excursionsLoading: state.excursionsLoading,
      }))
    )

  const [coordinates, setCoordinates] = useState<string>("-°N -°E")
  const [mapTransitioning, setMapTransitioning] = useState(false)

  const VESSEL_COLOR = [30, 224, 171]
  const TRACKED_VESSEL_COLOR = [30, 224, 171, 0]

  const isVesselSelected = (vp: VesselPosition) => {
    let vesselSelected = vp.vessel.id === activePosition?.vessel.id
    if (mapMode === "position") {
      vesselSelected = vesselSelected || trackedVesselIDs.includes(vp.vessel.id)
    }
    return vesselSelected
  }

  const trackedVessels = useMemo(() => {
    return vesselsPositions
      .map((vp) => vp.vessel)
      .filter((vessel) => trackedVesselIDs.includes(vessel.id))
  }, [vesselsPositions, trackedVesselIDs])

  const trackedAndShownVessels = useMemo(() => {
    return trackedVessels.filter(
      (vessel) => !vesselsIDsHidden.includes(vessel.id)
    )
  }, [trackedVessels, vesselsIDsHidden])

  const trackedAndShownExcursions = useMemo(() => {
    const trackedAndShownExcursions: VesselExcursion[] = []
    trackedAndShownVessels.forEach((vessel) => {
      const vesselExcursions = excursions[vessel.id] || []
      trackedAndShownExcursions.push(
        ...vesselExcursions.filter(
          (excursion) => !excursionsIDsHidden.includes(excursion.id)
        )
      )
    })
    return trackedAndShownExcursions
  }, [trackedAndShownVessels, excursions, excursionsIDsHidden])

  const onMapClick = ({ layer }: PickingInfo) => {
    if (layer?.id !== "vessels-latest-positions") {
      setActivePosition(null)
    }
  }

  const onVesselClick = ({ object }: PickingInfo) => {
    setActivePosition(object as VesselPosition)
  }

  const getVesselColor = (vp: VesselPosition) => {
    let colorRgb = VESSEL_COLOR
    let opacity = getOpacityFromTimestamp(vp.timestamp)

    if (isVesselSelected(vp)) {
      colorRgb = TRACKED_VESSEL_COLOR
      opacity = 0

    }

    if (mapMode === "track") {
      const listIndex = trackedVesselIDs.indexOf(vp.vessel.id)
      colorRgb = getVesselColorRGB(listIndex)
    }

    return [colorRgb[0], colorRgb[1], colorRgb[2], opacity]
  }

  const latestPositions = useMemo(() => {
    let displayedPositions = vesselsPositions
    if (mapMode === "track") {
      displayedPositions = displayedPositions.filter((vp) =>
        trackedVesselIDs.includes(vp.vessel.id)
      )
    }
    return new IconLayer<VesselPosition>({
      id: `vessels-latest-positions`,
      data: displayedPositions,
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
      getSize: (vp: VesselPosition) => {
        const length = vp.vessel.length || 0
        if (length > 80) return 18 // Large vessels
        if (length > 40) return 14 // Small vessels
        return 10 // Medium vessels (default)
      },
      getColor: (vp: VesselPosition) => {
        return new Uint8ClampedArray(getVesselColor(vp))
      },

      pickable: true,
      onClick: onVesselClick,
      updateTriggers: {
        getColor: [activePosition?.vessel.id, trackedVesselIDs],
      },
    })
  }, [
    mapMode,
    vesselsPositions,
    activePosition?.vessel.id,
    trackedVesselIDs,
    isVesselSelected,
  ])

  const [segmentsLayer, setSegmentsLayer] = useState<Layer[]>([])

  function getSegmentsColor(
    feature: Feature<Geometry, VesselExcursionSegmentGeo>
  ) {
    const listIndex = trackedVesselIDs.indexOf(feature.properties.vessel_id)
    return getVesselColorRGB(listIndex)
  }

  function toSegmentsGeo(
    vesselId: number,
    segments: VesselExcursionSegment[] | undefined
  ): VesselExcursionSegmentsGeo {
    if (!segments) return { type: "FeatureCollection", features: [] }
    const segmentsGeo = segments?.map((segment: VesselExcursionSegment) => {
      return {
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: [
            segment.start_position.coordinates,
            segment.end_position.coordinates,
          ],
        },
        properties: {
          vessel_id: vesselId,
          excursion_id: segment.excursion_id,
          speed: segment.average_speed,
          navigational_status: "unknown",
        },
      } as Feature<Geometry, VesselExcursionSegmentGeo>
    })
    return { type: "FeatureCollection", features: segmentsGeo ?? [] }
  }

  function onSegmentClick({ object }: PickingInfo) {
    const segment = object as Feature<Geometry, VesselExcursionSegmentGeo>
    if (focusedExcursionID !== segment.properties.excursion_id) {
      setFocusedExcursionID(segment.properties.excursion_id)
    } else {
      focusOnExcursion(segment.properties.excursion_id)
    }
    setLeftPanelOpened(true)
  }

  function excursionToSegmentsLayer(excursion: VesselExcursion) {
    const segmentsGeo = toSegmentsGeo(excursion.vessel_id, excursion.segments)
    return new GeoJsonLayer<VesselExcursionSegmentGeo>({
      id: `${excursion.vessel_id}_vessel_trail`,
      data: segmentsGeo,
      getFillColor: (feature) => {
        return getSegmentsColor(feature)
      },
      getLineColor: (feature) => {
        const color = getSegmentsColor(feature)
        return new Uint8ClampedArray(color)
      },
      pickable: true,
      stroked: false,
      filled: true,
      getLineWidth: 0.5,
      lineWidthMinPixels: 0.5,
      lineWidthMaxPixels: 3,
      lineWidthUnits: "pixels",
      lineWidthScale: 2,
      getPointRadius: 4,
      getTextSize: 12,
      onClick: onSegmentClick,
    })
  }

  useEffect(() => {
    if (mapMode === "track") {
      const layers: Layer[] = []

      trackedAndShownExcursions.forEach((excursion) => {
        layers.push(excursionToSegmentsLayer(excursion))
      })

      setSegmentsLayer(layers)
    } else {
      setSegmentsLayer([])
    }
  }, [mapMode, trackedAndShownExcursions, viewState])

  const onMapHover = ({ coordinate }: PickingInfo) => {
    coordinate &&
      setCoordinates(
        coordinate[1].toFixed(3).toString() +
          "°N " +
          coordinate[0].toFixed(3) +
          "°E"
      )
  }

  const focusOnExcursion = (excursionID: number) => {
    const focusedExcursion = Object.values(excursions)
      .flat()
      .find((excursion) => excursion.id === focusedExcursionID)

    if (focusedExcursion) {
      // Get all coordinates from excursion segments
      const coordinates = focusedExcursion?.segments?.map(
        (segment) => segment.start_position.coordinates
      )

      if (!coordinates) return

      // Find bounds
      const bounds = coordinates.reduce(
        (acc, coord) => {
          return {
            minLng: Math.min(acc.minLng, coord[0]),
            maxLng: Math.max(acc.maxLng, coord[0]),
            minLat: Math.min(acc.minLat, coord[1]),
            maxLat: Math.max(acc.maxLat, coord[1]),
          }
        },
        {
          minLng: Infinity,
          maxLng: -Infinity,
          minLat: Infinity,
          maxLat: -Infinity,
        }
      )

      // Add padding
      const padding = 0.5 // degrees
      bounds.minLng -= padding
      bounds.maxLng += padding
      bounds.minLat -= padding
      bounds.maxLat += padding

      // Calculate center and zoom
      const center = [
        (bounds.minLng + bounds.maxLng) / 2,
        (bounds.minLat + bounds.maxLat) / 2,
      ]

      const latDiff = bounds.maxLat - bounds.minLat
      const lngDiff = bounds.maxLng - bounds.minLng
      const zoom = Math.min(
        Math.floor(9 - Math.log2(Math.max(latDiff, lngDiff))),
        20 // max zoom
      )

      setViewState({
        ...viewState,
        longitude: center[0],
        latitude: center[1],
        zoom: zoom,
        transitionDuration: 500,
        onTransitionStart: () => setMapTransitioning(true),
        onTransitionEnd: () => setMapTransitioning(false),
      })
    }
  }

  useEffect(() => {
    if (focusedExcursionID) {
      focusOnExcursion(focusedExcursionID)
    }
  }, [focusedExcursionID])

  useEffect(() => {
    if (!mapTransitioning) {
      setFocusedExcursionID(null)
    }
  }, [viewState.latitude, viewState.longitude])

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
        !zonesLoading && [
          ampMultiZonesLayer,
          ampSingleZonesLayer,
          territorialZonesLayer,
          fishingZonesLayer,
        ],
        !vesselsLoading && !positionsLoading && segmentsLayer,
        !positionsLoading && latestPositions,
      ]
        .flat()
        .filter(Boolean) as Layer[],
    [
      zonesLoading,
      vesselsLoading,
      positionsLoading,
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
      controller={{
        dragRotate: false,
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