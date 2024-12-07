"use client"

import { useEffect, useMemo, useState } from "react"
import {
  getVesselExcursions,
  getVessels,
  getVesselSegments,
  getVesselsLatestPositions,
} from "@/services/backend-rest-client"

import { Vessel, VesselPosition } from "@/types/vessel"
import { ZoneWithGeometry } from "@/types/zone"
import Spinner from "@/components/ui/custom/spinner"
import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import Map from "@/components/core/map/main-map"
import PositionPreview from "@/components/core/map/position-preview"
import { useMapStore } from "@/components/providers/map-store-provider"

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
  const [isLoadingExcursions, setIsLoadingExcursions] = useState(false);

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
      // const zonesData = await fetchZones()
      setZones([])
      setIsLoadingZones(false)
    }
    if (zones.length === 0) {
      loadZones()
    }
  }, [isLoadingZones, zones.length])

  const {
    trackedVesselIDs,
    mode: mapMode,
    trackModeOptions,
    setTrackModeOptions,
  } = useMapStore((state) => state)

  const { startDate, endDate, vesselsIDsShown } = trackModeOptions;

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
      <LeftPanel vessels={vessels} isLoading={isLoadingVessels} />
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
      <MapControls />
      <PositionPreview />
      {isLoading && (
        <div className="absolute bottom-10 left-5">
          <Spinner className="text-white" />
        </div>
      )}
    </>
  )
}
