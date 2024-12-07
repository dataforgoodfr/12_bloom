"use client"

import { useEffect, useState } from "react"
import useSWR from "swr"

import { Vessel, VesselPosition } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import Map from "@/components/core/map/main-map"
import PositionPreview from "@/components/core/map/position-preview"

const fetcher = async (url: string) => {
  const response = await fetch(url, {
    cache: "force-cache",
  })
  return response.json()
}

export default function MapPage() {
  const { data: vessels = [], isLoading: isLoadingVessels } = useSWR<Vessel[]>(
    "/api/vessels",
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      keepPreviousData: true,
    }
  )

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

  const isLoading = isLoadingVessels || isLoadingPositions || isLoadingZones

  return (
    <>
      <LeftPanel vessels={vessels} isLoading={isLoadingVessels} />
      <Map
        vesselsPositions={latestPositions}
        zones={zones}
        isLoading={{
          vessels: isLoadingVessels,
          positions: isLoadingPositions,
          zones: isLoadingZones,
        }}
      />
      <MapControls zoneLoading={isLoading} />
      <PositionPreview />
    </>
  )
}
