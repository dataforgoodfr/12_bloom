"use client"

import { useEffect, useState } from "react"
import {
  getVessels,
  getVesselsLatestPositions,
} from "@/services/backend-rest-client"

import { Vessel, VesselPosition } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import Spinner from "@/components/ui/custom/spinner"
import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import Map from "@/components/core/map/main-map"
import PositionPreview from "@/components/core/map/position-preview"

async function fetchVessels() {
  try {
    const response = await fetch("/api/vessels", {
      cache: "force-cache",
    })
    return await response.json()
  } catch (error) {
    console.log("An error occurred while fetching vessels: " + error)
    return []
  }
}

async function fetchZones() {
  try {
    const response = await fetch("/api/zones", {
      cache: "force-cache",
    })
    return await response.json()
  } catch (error) {
    console.error("An error occurred while fetching zones:", error)
    return []
  }
}

export default function MapPage() {
  const [vessels, setVessels] = useState<Vessel[]>([])
  const [latestPositions, setLatestPositions] = useState<VesselPosition[]>([])
  const [zones, setZones] = useState<ZoneWithGeometry[]>([])
  const [isLoadingVessels, setIsLoadingVessels] = useState(true)
  const [isLoadingPositions, setIsLoadingPositions] = useState(true)
  const [isLoadingZones, setIsLoadingZones] = useState(true)

  useEffect(() => {
    const loadVessels = async () => {
      const vesselsData = await fetchVessels()
      setVessels(vesselsData)
      setIsLoadingVessels(false)
    }
    loadVessels()
  }, [])

  useEffect(() => {
    const loadPositions = async () => {
      const response = await fetch("/api/vessels/positions", {
        cache: "force-cache",
        next: { revalidate: 900 }, // 15 minutes
      })
      const positionsData = await response.json()
      setLatestPositions(positionsData)
      setIsLoadingPositions(false)
    }
    loadPositions()
  }, [])

  useEffect(() => {
    const loadZones = async () => {
      const zonesData = await fetchZones()
      setZones(zonesData)
      setIsLoadingZones(false)
    }
    if (zones.length === 0) {
      loadZones()
    }
  }, [isLoadingZones, zones.length])

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
