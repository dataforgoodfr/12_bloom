import { useMemo } from "react"
import { GeoJsonLayer, Layer, PolygonLayer } from "deck.gl"
import { useShallow } from "zustand/react/shallow"

import { ZoneCategory, ZoneWithGeometry } from "@/types/zone"
import { useLoaderStore, useMapStore } from "@/libs/stores"

export interface ZonesLayerProps {
  zones: ZoneWithGeometry[]
  filtersDisabled?: boolean
}

export const useZonesLayer = ({
  zones,
  filtersDisabled = false,
}: ZonesLayerProps): Layer[] => {
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

  const isAmpDisplayed = filtersDisabled
    ? true
    : displayedZones.includes(ZoneCategory.AMP)

  const isTerritorialDisplayed = filtersDisabled
    ? true
    : displayedZones.includes(ZoneCategory.TERRITORIAL_SEAS)

  const isFishingDisplayed = filtersDisabled
    ? true
    : displayedZones.includes(ZoneCategory.FISHING_COASTAL_WATERS)

  console.log("zones", zones)
  console.log("isAmpDisplayed", isAmpDisplayed)
  console.log("isTerritorialDisplayed", isTerritorialDisplayed)
  console.log("isFishingDisplayed", isFishingDisplayed)

  const ampMultiZones = useMemo(() => {
    const filteredZones = isAmpDisplayed
      ? zones
          .filter((z) => z.category === ZoneCategory.AMP)
          .filter((z) => z.geometry.type === "MultiPolygon")
      : []
    return filteredZones
  }, [zones, isAmpDisplayed])

  const ampSingleZones = useMemo(() => {
    const filteredZones = isAmpDisplayed
      ? zones
          .filter((z) => z.category === ZoneCategory.AMP)
          .filter((z) => z.geometry.type === "Polygon")
      : []
    return filteredZones
  }, [zones, isAmpDisplayed])

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
        visible: isAmpDisplayed,
      }),
    [ampMultiZones, isAmpDisplayed]
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
        visible: isAmpDisplayed,
      }),
    [ampSingleZones, isAmpDisplayed]
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
        getLineColor: [20, 81, 6, 255],
        getLineWidth: 1,
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

  console.log("zonesLoading", zonesLoading)

  if (zonesLoading) return []

  return [
    ampMultiZonesLayer,
    ampSingleZonesLayer,
    territorialZonesLayer,
    fishingZonesLayer,
  ]
}
