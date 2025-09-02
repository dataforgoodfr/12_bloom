import { useCallback, useMemo } from "react"
import { IconLayer, PickingInfo } from "deck.gl"
import { useShallow } from "zustand/react/shallow"

import { VesselPosition } from "@/types/vessel"
import { getVesselColorRGB } from "@/libs/colors"
import {
  useLoaderStore,
  useMapStore,
  useTrackModeOptionsStore,
  useVesselsStore,
} from "@/libs/stores"

import { getDeckGLIconMapping, VesselIconName } from "../utils"

export const useVesselsLayers = () => {
  const VESSEL_COLOR = [94, 141, 185]
  const TRACKED_VESSEL_COLOR = [30, 224, 171]

  const { vesselsLoading, positionsLoading } = useLoaderStore(
    useShallow((state) => ({
      vesselsLoading: state.vesselsLoading,
      positionsLoading: state.positionsLoading,
    }))
  )

  const { trackedVesselIDs, vesselsIDsHidden } = useTrackModeOptionsStore(
    useShallow((state) => ({
      vesselsIDsHidden: state.vesselsIDsHidden,
      trackedVesselIDs: state.trackedVesselIDs,
    }))
  )

  const {
    mode: mapMode,
    activePosition,
    latestPositions: vesselsPositions,
    setActivePosition,
  } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      activePosition: state.activePosition,
      latestPositions: state.latestPositions,
      setActivePosition: state.setActivePosition,
    }))
  )

  const { typeFilter, classFilter, countryFilter } = useVesselsStore(
    useShallow((state) => ({
      typeFilter: state.typeFilter,
      classFilter: state.classFilter,
      countryFilter: state.countryFilter,
    }))
  )

  const isVesselSelected = (vp: VesselPosition) => {
    let vesselSelected = vp.vessel.id === activePosition?.vessel.id
    if (mapMode === "position") {
      vesselSelected = vesselSelected || trackedVesselIDs.includes(vp.vessel.id)
    }
    return vesselSelected
  }

  const onVesselClick = ({ object }: PickingInfo) => {
    setActivePosition(object as VesselPosition)
  }

  const getVesselOpacityFromTimestamp = (timestamp: string) => {
    const now = new Date()
    const positionTime = new Date(timestamp)
    const diffInHours =
      (now.getTime() - positionTime.getTime()) / (1000 * 60 * 60)

    if (diffInHours <= 0.75) return 255 // 100% opacity
    if (diffInHours <= 3) return 179 // 70% opacity
    if (diffInHours <= 5) return 140 // 55% opacity
    return 102 // 40% opacity
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
      opacity = getVesselOpacityFromTimestamp(vp.timestamp)
    }

    return [colorRgb[0], colorRgb[1], colorRgb[2], opacity]
  }

  const deckGLIconMapping = useMemo(() => {
    return getDeckGLIconMapping()
  }, [])

  const getVesselLayer = ({
    id,
    outlined,
    positions,
    color,
  }: {
    id: string
    outlined: boolean
    positions: VesselPosition[]
    color?: number[]
  }) => {
    return new IconLayer<VesselPosition>({
      id,
      data: positions,
      getPosition: (vp: VesselPosition) => [
        vp?.position?.coordinates[0],
        vp?.position?.coordinates[1],
      ],
      getAngle: (vp: VesselPosition) => {
        return vp.heading ? 365 - Math.round(vp.heading) : 0
      },
      getIcon: (vp: VesselPosition): VesselIconName => {
        let iconName = vp.heading ? "withHeading" : "noHeading"
        if (outlined) {
          iconName += "Outline"
        }
        return iconName as VesselIconName
      },
      iconAtlas: "../../../img/vessel_atlas.png",
      iconMapping: deckGLIconMapping,
      getSize: (vp: VesselPosition) => {
        const length = vp.vessel.length || 0
        const type = vp.heading ? "arrow" : "ellipse"
        if (length > 80) return type == "arrow" ? 48 : 20 // Large vessels
        if (length > 40) return type == "arrow" ? 38 : 16 // Medium vessels
        return type == "arrow" ? 32 : 14 // Small vessels (default)
      },
      getColor: (vp: VesselPosition) => {
        if (!color) {
          return new Uint8ClampedArray(getVesselColor(vp))
        }

        if (color.length === 4) {
          return new Uint8ClampedArray(color)
        }

        if (color.length === 3) {
          const opacity = getVesselOpacityFromTimestamp(vp.timestamp)
          return new Uint8ClampedArray([...color, opacity])
        }

        return new Uint8ClampedArray(getVesselColor(vp))
      },
      pickable: true,
      onClick: onVesselClick,
      updateTriggers: {
        getColor: [activePosition?.vessel.id, trackedVesselIDs],
      },
    })
  }

  const getVesselSelectedLayer = () => {
    const selectedVessel = vesselsPositions.find(
      (vp) => vp.vessel.id === activePosition?.vessel.id
    )

    return new IconLayer<VesselPosition>({
      id: `vessels-selected-position`,
      data: [selectedVessel],
      getPosition: (vp: VesselPosition) => [
        vp?.position?.coordinates[0],
        vp?.position?.coordinates[1],
      ],
      iconAtlas: "../../../img/vessel_atlas.png",
      iconMapping: deckGLIconMapping,
      getIcon: (vp: VesselPosition) => "selectionHalo",
      getSize: (vp: VesselPosition) => 40,
      getColor: (vp: VesselPosition) => {
        return new Uint8ClampedArray(getVesselColor(vp))
      },
    })
  }

  const vesselsLayer = useMemo(() => {
    let displayedPositions: VesselPosition[] = []
    if (mapMode === "track") {
      displayedPositions = vesselsPositions.filter(
        (vp) =>
          trackedVesselIDs.includes(vp.vessel.id) &&
          !vesselsIDsHidden.includes(vp.vessel.id)
      )
    }

    if (mapMode === "position") {
      displayedPositions = vesselsPositions

      // Apply filters
      displayedPositions = displayedPositions.filter((vp) => {
        const { type, length_class, country_iso3 } = vp.vessel
        const matchesType =
          typeFilter.length === 0 || (type && typeFilter.includes(type))
        const matchesClass =
          classFilter.length === 0 ||
          (length_class && classFilter.includes(length_class))
        const matchesCountry =
          countryFilter.length === 0 ||
          (country_iso3 && countryFilter.includes(country_iso3))
        return matchesType && matchesClass && matchesCountry
      })
    }

    const layers = [
      getVesselLayer({
        id: "vessels-latest-positions",
        outlined: false,
        positions: displayedPositions,
      }),
      getVesselLayer({
        id: "vessels-latest-positions-outlined",
        outlined: true,
        positions: displayedPositions,
        color: [20, 40, 58],
      }),
    ]
    if (activePosition) {
      const selectedLayer = getVesselSelectedLayer()
      layers.push(selectedLayer)
    }

    return layers
  }, [
    mapMode,
    vesselsPositions,
    activePosition?.vessel.id,
    trackedVesselIDs,
    isVesselSelected,
  ])

  if (vesselsLoading || positionsLoading) return []

  return vesselsLayer
}
