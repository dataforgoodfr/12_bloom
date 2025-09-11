"use client";

import { useEffect } from "react";
import { getVesselExcursions, getVesselExcursionsExtracts, getVesselSegments, getVesselTimeByZone } from "@/services/backend-rest-client";
import useSWR from "swr";
import { useShallow } from "zustand/react/shallow";



import { Port } from "@/types/port";
import { Vessel, VesselPosition } from "@/types/vessel";
import { ZoneCategory, ZoneWithGeometry } from "@/types/zone";
import { useLoaderStore } from "@/libs/stores/loader-store";
import { useMapStore } from "@/libs/stores/map-store";
import { usePortsStore } from "@/libs/stores/port-store";
import { useTrackModeOptionsStore } from "@/libs/stores/track-mode-options-store";
import { useVesselsStore } from "@/libs/stores/vessels-store";
import LeftPanel from "@/components/core/left-panel/main";
import MapControls from "@/components/core/map-controls";
import Map from "@/components/core/map/main-map";





const fetcher = async (url: string) => {
  const response = await fetch(url)
  return response.json()
}

export default function MapPage() {
  const setVessels = useVesselsStore((state) => state.setVessels)

  const {
    setZonesLoading,
    setPositionsLoading,
    setVesselsLoading,
    setExcursionsLoading,
    setPortsLoading,
  } = useLoaderStore(
    useShallow((state) => ({
      setZonesLoading: state.setZonesLoading,
      setPositionsLoading: state.setPositionsLoading,
      setVesselsLoading: state.setVesselsLoading,
      setExcursionsLoading: state.setExcursionsLoading,
      setPortsLoading: state.setPortsLoading,
    }))
  )

  const { mode: mapMode, setLatestPositions } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      setLatestPositions: state.setLatestPositions,
    }))
  )

  const setPorts = usePortsStore((state) => state.setPorts)

  const { data: vessels = [], isLoading: isLoadingVessels } = useSWR<Vessel[]>(
    "/api/vessels",
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      keepPreviousData: true,
    }
  )

  const { data: ports = [], isLoading: isLoadingPorts } = useSWR<Port[]>(
    "/api/ports",
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      keepPreviousData: true,
    }
  )

  useEffect(() => {
    if (!isLoadingPorts) {
      setPorts(ports)
    }
  }, [ports, isLoadingPorts])

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
  }, [isLoadingZones])

  useEffect(() => {
    setPositionsLoading(isLoadingPositions)
  }, [isLoadingPositions])

  useEffect(() => {
    setVesselsLoading(isLoadingVessels)
  }, [isLoadingVessels])

  useEffect(() => {
    setPortsLoading(isLoadingPorts)
  }, [isLoadingPorts])

  useEffect(() => {
    const resetExcursions = async () => {
      setExcursionsLoading(true)
      for (const vesselID of trackedVesselIDs) {
        const vesselExcursionsSummary = await getVesselExcursionsExtracts(
          vesselID,
          startDate,
          endDate
        )


        const vesselExcursions = vesselExcursionsSummary.data.excursions
        for (const excursion of vesselExcursions) {
          const segments = await getVesselSegments(
            vesselID,
            excursion.excursion_id
          )
          excursion.segments = segments.data

          const timeByMPAZone = await getVesselTimeByZone({
            vesselId: vesselID,
            category: ZoneCategory.AMP,
            startAt: startDate ? startDate > new Date(excursion.departure_at) ? new Date(startDate) : new Date(excursion.departure_at) : undefined,
            endAt: endDate ? endDate < new Date(excursion.arrival_at!) ? new Date(endDate) : new Date(excursion.arrival_at!) : undefined,
          })
          excursion.timeByMPAZone = timeByMPAZone
          console.log("timeByMPAZone", timeByMPAZone)
        }
        setVesselExcursions(vesselID, vesselExcursions)
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
      <Map zones={zones} ports={ports} />
      <MapControls
        zoneLoading={isLoadingZones}
        vesselLoading={isLoadingVessels}
      />
    </>
  )
}