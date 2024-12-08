"use client"

import { useEffect, useMemo, useState } from "react"
import {
  getVesselExcursions,
  getVessels,
  getVesselSegments,
  getVesselsLatestPositions,
} from "@/services/backend-rest-client"
import useSWR from "swr"
import { useShallow } from 'zustand/react/shallow'

import { Vessel, VesselPosition } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import Map from "@/components/core/map/main-map"
import PositionPreview from "@/components/core/map/position-preview"
import { useMapStore } from "@/libs/stores/map-store"
import { useVesselsStore } from "@/libs/stores/vessels-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"

const fetcher = async (url: string) => {
  const response = await fetch(url, {
    cache: "force-cache",
  })
  return response.json()
}

export default function MapPage() {
  const setVessels = useVesselsStore((state) => state.setVessels)

  const mapMode = useMapStore((state) => state.mode)
  const { startDate, endDate, trackedVesselIDs } = useTrackModeOptionsStore(useShallow((state) => ({
    startDate: state.startDate,
    endDate: state.endDate,
    trackedVesselIDs: state.trackedVesselIDs,
  })))

  const { data: vessels = [], isLoading: isLoadingVessels } = useSWR<Vessel[]>(
    "/api/vessels",
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      keepPreviousData: true,
    }
  )

  useEffect(() => {
    if (!isLoadingVessels) {
      setVessels(vessels);
    }
  }, [vessels, isLoadingVessels]);

  const { data: zones = [], isLoading: isLoadingZones } = useSWR<
    ZoneWithGeometry[]
  >("/api/zones", fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    keepPreviousData: true,
  })

  const { data: latestPositions = [], isLoading: isLoadingPositions } = useSWR<
    VesselPosition[]
  >("/api/vessels/positions", fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    keepPreviousData: true,
    revalidateOnMount: true,
    refreshInterval: 900000, // 15 minutes in milliseconds
  })

  const [isLoadingExcursions, setIsLoadingExcursions] = useState(false);

  const vesselsWithExcursionsTimeframeShown = useMemo(() => {
    return vessels.filter((vessel) => trackedVesselIDs.includes(vessel.id) && vessel.excursions_timeframe?.mapVisibility !== false);
  }, [vessels, trackedVesselIDs]);

  useEffect(() => {
    const resetExcursions = async () => {
      setIsLoadingExcursions(true);
      for (const vessel of vesselsWithExcursionsTimeframeShown) {
        if (!vessel.excursions_timeframe || vessel.excursions_timeframe.startDate !== startDate || vessel.excursions_timeframe.endDate !== endDate) {
          const excursions = await getVesselExcursions(vessel.id, startDate, endDate);
          vessel.excursions_timeframe = {
            startDate,
            endDate,
            excursions: excursions.data
          };

          for (const excursion of vessel.excursions_timeframe.excursions) {
            const segments = await getVesselSegments(vessel.id, excursion.id);
            excursion.segments = segments.data;
          }
        }
      }
      setIsLoadingExcursions(false);
    }
    if (mapMode === "track") {
      resetExcursions();
    }
  }, [startDate, endDate, mapMode, vesselsWithExcursionsTimeframeShown])

  const isLoading = isLoadingVessels || isLoadingPositions || isLoadingZones || isLoadingExcursions

  return (
    <>
      <LeftPanel isLoading={isLoadingVessels} />
      <Map
        vesselsPositions={latestPositions}
        zones={zones}
        isLoading={{
          vessels: isLoadingVessels,
          positions: isLoadingPositions,
          zones: isLoadingZones,
          excursions: isLoadingExcursions,
        }}
      />
      <MapControls zoneLoading={isLoading} />
      <PositionPreview />
    </>
  )
}
