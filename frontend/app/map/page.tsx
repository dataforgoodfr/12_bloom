"use client"

import { useEffect, useMemo, useState } from "react"
import {
  getVesselExcursions,
  getVessels,
  getVesselSegments,
  getVesselsLatestPositions,
  getVesselTimeByZone,
} from "@/services/backend-rest-client"
import useSWR from "swr"
import { useShallow } from "zustand/react/shallow"

import { Vessel, VesselPosition } from "@/types/vessel"
import { ZoneCategory, ZoneWithGeometry } from "@/types/zone"
import { useLoaderStore } from "@/libs/stores/loader-store"
import { useMapStore } from "@/libs/stores/map-store"
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store"
import { useVesselsStore } from "@/libs/stores/vessels-store"
import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import Map from "@/components/core/map/main-map"

const fetcher = async (url: string) => {
  const response = await fetch(url, {
    cache: "force-cache",
  })
  return response.json()
}

export default function MapPage() {
  const setVessels = useVesselsStore((state) => state.setVessels)

  const {
    setZonesLoading,
    setPositionsLoading,
    setVesselsLoading,
    setExcursionsLoading,
  } = useLoaderStore(
    useShallow((state) => ({
      setZonesLoading: state.setZonesLoading,
      setPositionsLoading: state.setPositionsLoading,
      setVesselsLoading: state.setVesselsLoading,
      setExcursionsLoading: state.setExcursionsLoading,
    }))
  )

  const { mode: mapMode, setLatestPositions } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      setLatestPositions: state.setLatestPositions,
    }))
  )

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
      setVessels(vessels)
    }
  }, [vessels, isLoadingVessels])

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

  useEffect(() => {
    setLatestPositions(latestPositions)
  }, [latestPositions])

  const { startDate, endDate, trackedVesselIDs, setVesselExcursions } =
    useTrackModeOptionsStore(
      useShallow((state) => ({
        startDate: state.startDate,
        endDate: state.endDate,
        trackedVesselIDs: state.trackedVesselIDs,
        setVesselExcursions: state.setVesselExcursions,
      }))
    )

  useEffect(() => {
    setZonesLoading(isLoadingZones)
    setPositionsLoading(isLoadingPositions)
    setVesselsLoading(isLoadingVessels)
  }, [isLoadingZones, isLoadingPositions, isLoadingVessels])

  useEffect(() => {
    const resetExcursions = async () => {
      setExcursionsLoading(true)
      for (const vesselID of trackedVesselIDs) {
        const vesselExcursions = await getVesselExcursions(
          vesselID,
          startDate,
          endDate
        )
        for (const excursion of vesselExcursions.data) {
          const segments = await getVesselSegments(vesselID, excursion.id)
          excursion.segments = segments.data

          const timeByMPAZone = await getVesselTimeByZone({
            vesselId: vesselID,
            category: ZoneCategory.AMP,
            startAt: excursion.departure_at
              ? new Date(excursion.departure_at)
              : undefined,
            endAt: excursion.arrival_at
              ? new Date(excursion.arrival_at)
              : undefined,
          })
          excursion.timeByMPAZone = timeByMPAZone
        }
        setVesselExcursions(vesselID, vesselExcursions.data)
      }
      setExcursionsLoading(false)
    }
    if (mapMode === "track") {
      resetExcursions()
    }
  }, [startDate, endDate, mapMode, trackedVesselIDs])

  return (
    <>
      <LeftPanel />
      <Map zones={zones} />
      <MapControls zoneLoading={isLoadingZones} />
    </>
  )
}
