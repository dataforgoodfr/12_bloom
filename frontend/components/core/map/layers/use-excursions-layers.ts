import { useEffect, useMemo } from "react"
import { PathStyleExtension } from "@deck.gl/extensions"
import { GeoJsonLayer, IconLayer, Layer, PickingInfo } from "deck.gl"
import type { Feature, Geometry } from "geojson"
import { useShallow } from "zustand/react/shallow"

import {
  SegmentVesselPosition,
  VesselExcursion,
  VesselExcursionSegment,
  VesselExcursionSegmentGeo,
  VesselExcursionSegmentsGeo,
} from "@/types/vessel"
import { getVesselColorRGB } from "@/libs/colors"
import {
  useLoaderStore,
  useMapStore,
  useTrackModeOptionsStore,
} from "@/libs/stores"

export const useExcursionsLayers = () => {
  const {
    trackedVesselIDs,
    vesselsIDsHidden,
    excursions,
    excursionsIDsHidden,
    focusedExcursionID,
    showPositions,
    segmentMode,
    setFocusedExcursionID,
  } = useTrackModeOptionsStore(
    useShallow((state) => ({
      trackedVesselIDs: state.trackedVesselIDs,
      vesselsIDsHidden: state.vesselsIDsHidden,
      excursionsIDsHidden: state.excursionsIDsHidden,
      excursions: state.excursions,
      focusedExcursionID: state.focusedExcursionID,
      showPositions: state.showPositions,
      segmentMode: state.segmentMode,
      setFocusedExcursionID: state.setFocusedExcursionID,
    }))
  )

  const {
    mode: mapMode,
    viewState,
    latestPositions: vesselsPositions,
    setViewState,
    setLeftPanelOpened,
  } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      viewState: state.viewState,
      latestPositions: state.latestPositions,
      setViewState: state.setViewState,
      setLeftPanelOpened: state.setLeftPanelOpened,
    }))
  )

  const { excursionsLoading } = useLoaderStore(
    useShallow((state) => ({
      excursionsLoading: state.excursionsLoading,
    }))
  )

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

  function getColorFromSpeed(speed?: number) {
    const highSpeed = 20
    const highSpeedColor = [239, 68, 68]

    const lowSpeed = 0
    const lowSpeedColor = [234, 179, 8]

    const grayColor = [128, 128, 128, 255]

    if (speed === undefined) return grayColor // Gray for undefined speed

    const ratio = Math.min(
      Math.max((speed - lowSpeed) / (highSpeed - lowSpeed), 0),
      1
    )
    const red = Math.round(
      lowSpeedColor[0] +
        Math.min(Math.max(ratio, 0), 1) * (highSpeedColor[0] - lowSpeedColor[0])
    )
    const green = Math.round(
      lowSpeedColor[1] +
        Math.min(Math.max(ratio, 0), 1) * (highSpeedColor[1] - lowSpeedColor[1])
    )
    const blue = Math.round(
      lowSpeedColor[2] +
        Math.min(Math.max(ratio, 0), 1) * (highSpeedColor[2] - lowSpeedColor[2])
    )
    return [red, green, blue, 255]
  }

  function getSegmentColor(
    feature: Feature<Geometry, VesselExcursionSegmentGeo>
  ) {
    if (segmentMode === "vessel") {
      const listIndex = trackedVesselIDs.indexOf(feature.properties.vessel_id)
      return getVesselColorRGB(listIndex)
    } else if (segmentMode === "speed") {
      return getColorFromSpeed(feature.properties.speed)
    }
    return [255, 255, 255, 255]
  }

  function getSegmentWidth(
    feature: Feature<Geometry, VesselExcursionSegmentGeo>
  ) {
    if (feature.properties.type === "FISHING") {
      return 4
    }
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
          type: segment.type,
        },
      } as Feature<Geometry, VesselExcursionSegmentGeo>
    })
    return { type: "FeatureCollection", features: segmentsGeo ?? [] }
  }

  const focusOnExcursion = (excursionID: number) => {
    const focusedExcursion = Object.values(excursions)
      .flat()
      .find((excursion) => excursion.id === excursionID)

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

      if (
        viewState.longitude === center[0] &&
        viewState.latitude === center[1] &&
        viewState.zoom === zoom
      ) {
      }

      setViewState({
        ...viewState,
        longitude: center[0],
        latitude: center[1],
        zoom: zoom,
        transitionDuration: 500,
      })
    }
  }

  function onSegmentClick({ object }: PickingInfo) {
    const segment = object as Feature<Geometry, VesselExcursionSegmentGeo>
    if (segment.properties.excursion_id !== focusedExcursionID) {
      setFocusedExcursionID(segment.properties.excursion_id)
    } else {
      focusOnExcursion(segment.properties.excursion_id)
    }
    setLeftPanelOpened(true)
  }

  useEffect(() => {
    if (focusedExcursionID) {
      focusOnExcursion(focusedExcursionID)
    }
  }, [focusedExcursionID])

  function getDashArray(feature: Feature<Geometry, VesselExcursionSegmentGeo>) {
    if (feature.properties.type === "DEFAULT_AIS") {
      return [3, 4]
    }
    return [0, 0]
  }

  function excursionToSegmentsLayer(excursion: VesselExcursion) {
    const segmentsGeo = toSegmentsGeo(excursion.vessel_id, excursion.segments)
    return new GeoJsonLayer<VesselExcursionSegmentGeo>({
      id: `${excursion.vessel_id}_vessel_trail`,
      data: segmentsGeo,
      getFillColor: (feature) => {
        return getSegmentColor(feature)
      },
      getLineColor: (feature) => {
        const color = getSegmentColor(feature)
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

      // @ts-ignore
      getDashArray,
      extensions: [new PathStyleExtension({ dash: true })],
    })
  }

  const positionsLayer = useMemo(() => {
    const positions: SegmentVesselPosition[] = []
    trackedAndShownExcursions.forEach((excursion) => {
      if (!excursion.segments) return

      excursion.segments.forEach((segment) => {
        positions.push({
          type: "segmentPosition",
          timestamp: segment.timestamp_start,
          vessel_id: excursion.vessel_id,
          position: segment.start_position.coordinates,
          heading: segment.heading_at_start,
          speed: segment.speed_at_start,
        })
      })
    })
    return new IconLayer({
      id: "excursions-vessel-positions",
      data: positions,
      getPosition: (d: SegmentVesselPosition) => [
        d?.position[0],
        d?.position[1],
      ],
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
      pickable: true,
      getIcon: (d: SegmentVesselPosition) => {
        if (d.heading) {
          return "withHeading"
        }
        return "noHeading"
      },
      getColor: (d: SegmentVesselPosition) => {
        const color = getVesselColorRGB(trackedVesselIDs.indexOf(d.vessel_id))
        return new Uint8ClampedArray(color)
      },
      getSize: 20,
      getAngle: (d: SegmentVesselPosition) =>
        d.heading ? 365 - Math.round(d.heading) : 0,
    })
  }, [trackedAndShownExcursions, trackedVesselIDs, viewState, showPositions])

  const excursionsLayers = useMemo(() => {
    let layers: Layer[] = []

    if (mapMode === "track") {
      layers = trackedAndShownExcursions.map((excursion) => {
        return excursionToSegmentsLayer(excursion)
      })

      if (showPositions) {
        layers.push(positionsLayer)
      }
    } else {
      layers = []
    }

    return layers
  }, [
    mapMode,
    trackedAndShownExcursions,
    segmentMode,
    showPositions,
    viewState,
  ])

  if (excursionsLoading) return []

  return excursionsLayers
}
