import { useCallback, useMemo } from "react"
import { GeoJsonLayer, Layer, PolygonLayer } from "deck.gl"
import { useShallow } from "zustand/react/shallow"

import { ZoneCategory, ZoneWithGeometry } from "@/types/zone"
import { useLoaderStore, useMapStore } from "@/libs/stores"

export interface ZonesLayerProps {
  zones: ZoneWithGeometry[]
}

export const useZonesLayer = ({ zones }: ZonesLayerProps): Layer[] => {
  const { zonesLoading } = useLoaderStore(
    useShallow((state) => ({
      zonesLoading: state.zonesLoading,
    }))
  )

  const { displayedZones } = useMapStore(
    useShallow((state) => ({
      displayedZones: state.displayedZones,
    }))
  )

  const isZoneTypeDisplayed = useCallback(
    (zoneType: ZoneCategory) => {
      return displayedZones.includes(zoneType)
    },
    [displayedZones]
  )

  const isAMPDisplayed = displayedZones.includes(ZoneCategory.AMP)
  const isTerritorialDisplayed = displayedZones.includes(
    ZoneCategory.TERRITORIAL_SEAS
  )
  const isFishingDisplayed = displayedZones.includes(
    ZoneCategory.FISHING_COASTAL_WATERS
  )

  const ampMultiZones = useMemo(() => {
    const filteredZones = isZoneTypeDisplayed(ZoneCategory.AMP)
      ? zones
          .filter((z) => z.category === ZoneCategory.AMP)
          .filter((z) => z.geometry.type === "MultiPolygon")
      : []
    return filteredZones
  }, [zones, isZoneTypeDisplayed])

  const ampSingleZones = useMemo(() => {
    const filteredZones = isZoneTypeDisplayed(ZoneCategory.AMP)
      ? zones
          .filter((z) => z.category === ZoneCategory.AMP)
          .filter((z) => z.geometry.type === "Polygon")
      : []
    return filteredZones
  }, [zones, isZoneTypeDisplayed])

  const territorialZones = useMemo(
    () =>
      isTerritorialDisplayed
        ? zones.filter((z) => z.category === ZoneCategory.TERRITORIAL_SEAS)
        : [],
    [zones, isTerritorialDisplayed]
  )
  const fishingZones = useMemo(
    () =>
      isFishingDisplayed
        ? zones.filter(
            (z) => z.category === ZoneCategory.FISHING_COASTAL_WATERS
          )
        : [],
    [zones, isFishingDisplayed]
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

  if (zonesLoading) return []

  return [
    ampMultiZonesLayer,
    ampSingleZonesLayer,
    territorialZonesLayer,
    fishingZonesLayer,
  ]
}
