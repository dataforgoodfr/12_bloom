"use client"

import "maplibre-gl/dist/maplibre-gl.css"

import { useEffect, useMemo, useState } from "react"
import type { PickingInfo } from "@deck.gl/core"
import { GeoJsonLayer } from "@deck.gl/layers"
import DeckGL from "@deck.gl/react"
import { IconLayer, Layer, MapViewState, PolygonLayer } from "deck.gl"
import type { Feature, Geometry } from "geojson"
import { renderToString } from "react-dom/server"
import { Map as MapGL } from "react-map-gl/maplibre"
import { useShallow } from "zustand/react/shallow"

import {
  VesselExcursion,
  VesselExcursionSegment,
  VesselExcursionSegmentGeo,
  VesselExcursionSegmentsGeo,
  VesselPosition,
} from "@/types/vessel"
import { ZoneCategory, ZoneWithGeometry } from "@/types/zone"
import { getVesselColorRGB } from "@/libs/colors"
import { useLoaderStore } from "@/libs/stores/loader-store"
import { useMapStore } from "@/libs/stores/map-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import MapVesselTooltip from "@/components/ui/map-vessel-tooltip"
import MapZoneTooltip from "@/components/ui/map-zone-tooltip"

type DeckGLMapProps = {
  zones: ZoneWithGeometry[]
  onHover?: (info: PickingInfo) => void
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
  if (diffInHours <= 3) return 179 // 70% opacity
  if (diffInHours <= 5) return 140 // 55% opacity
  return 102 // 40% opacity
}

export default function DeckGLMap({
  zones,
  onHover,
}: DeckGLMapProps) {
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
    latestPositions: vesselsPositions,
    setActivePosition,
    setViewState,
    setLeftPanelOpened,
  } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      viewState: state.viewState,
      activePosition: state.activePosition,
      displayedZones: state.displayedZones,
      latestPositions: state.latestPositions,
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

  const [mapTransitioning, setMapTransitioning] = useState(false)

  const VESSEL_COLOR = [94, 141, 185]
  const TRACKED_VESSEL_COLOR = [30, 224, 171]

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
      setFocusedExcursionID(null)
    }
  }

  const onVesselClick = ({ object }: PickingInfo) => {
    setActivePosition(object as VesselPosition)
  }

  const getVesselColor = (vp: VesselPosition) => {
    let colorRgb = VESSEL_COLOR

    if (isVesselSelected(vp)) {
      colorRgb = TRACKED_VESSEL_COLOR
    }

    if (mapMode === "track") {
      const listIndex = trackedVesselIDs.indexOf(vp.vessel.id)
      colorRgb = getVesselColorRGB(listIndex)
    }

    let opacity = 255
    if (mapMode === "position") {
      opacity = getOpacityFromTimestamp(vp.timestamp)
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
        vp.heading ? 365 - Math.round(vp.heading) : 0,
      getIcon: (vp : VesselPosition) => {
        if (vp.heading) {
          return vp.vessel.id === activePosition?.vessel.id ? "selectedWithHeading" : "withHeading"
        } else {
          return vp.vessel.id === activePosition?.vessel.id ? "selectedNoHeading" : "noHeading"
        }
      },
      iconAtlas: "../../../img/vessel_atlas.png",
      iconMapping: {
        noHeading: {
          x: 0,
          y: 0,
          width: 32,
          height: 32,
          anchorY: 16,
          mask: true,
        },
        selectedNoHeading: {
          x: 32,
          y: 0,
          width: 32,
          height: 32,
          anchorX: 16,
          anchorY: 16,
          mask: true,
        },
        selectedWithHeading: {
          x: 64,
          y: 0,
          width: 32,
          height: 32,
          anchorX: 16,
          anchorY: 16,
          mask: true,
        },
        withHeading: {
          x: 96,
          y: 0,
          width: 32,
          height: 32,
          anchorX: 16,
          anchorY: 16,
          mask: true,
        },
      },
      getSize: (vp: VesselPosition) => {
        const length = vp.vessel.length || 0
        const type = vp.heading ? "arrow" : "ellipse"
        if (length > 80) return type == "arrow" ? 48 : 20 // Large vessels
        if (length > 40) return type == "arrow" ? 38 : 16 // Medium vessels
        return type == "arrow" ? 32 : 14 // Small vessels (default)
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

  function getSegmentWidth(
    feature: Feature<Geometry, VesselExcursionSegmentGeo>
  ) {
    return focusedExcursionID === feature.properties.excursion_id ? 3 : 1
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
    console.log("onSegmentClick", object)
    const segment = object as Feature<Geometry, VesselExcursionSegmentGeo>
    if (segment.properties.excursion_id !== focusedExcursionID) {
      console.log("setFocusedExcursionID", segment.properties.excursion_id)
      setFocusedExcursionID(segment.properties.excursion_id)
    } else {
      console.log("focusOnExcursion", segment.properties.excursion_id)
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
      getLineWidth: getSegmentWidth,
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
  }, [mapMode, trackedAndShownExcursions, viewState, focusedExcursionID])

  const onMapHover = (info: PickingInfo) => {
    onHover && onHover(info)
  }

  const focusOnExcursion = (excursionID: number) => {
    const focusedExcursion = Object.values(excursions)
      .flat()
      .find((excursion) => excursion.id === excursionID)

    if (focusedExcursion) {
      setMapTransitioning(true)
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

      if (
        viewState.longitude === center[0] &&
        viewState.latitude === center[1] &&
        viewState.zoom === zoom
      ) {
        setMapTransitioning(false)
      }

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

  // useEffect(() => {
  //   if (!mapTransitioning) {
  //     setFocusedExcursionID(null)
  //   }
  // }, [viewState.latitude, viewState.longitude])

  const getObjectType = (
    object: VesselPosition | ZoneWithGeometry | GeoJsonLayer | undefined
  ) => {
    if (!object) return null

    // @ts-ignore
    if (object?.properties?.excursion_id) {
      return "excursion"
    }

    if ("vessel" in object) {
      return "vessel"
    }

    if ("geometry" in object) {
      return "zone"
    }

    return null
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
  }: Partial<
    PickingInfo<VesselPosition | ZoneWithGeometry | GeoJsonLayer>
  >) => {
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
      element = <MapVesselTooltip vesselInfo={vesselInfo} />
    } else if (objectType === "zone") {
      const zoneInfo = object as ZoneWithGeometry
      element = <MapZoneTooltip zoneInfo={zoneInfo} />
    } else {
      return null
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
    </DeckGL>
  )
}
