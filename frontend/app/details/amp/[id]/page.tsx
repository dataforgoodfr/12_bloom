"use client";

import { useEffect, useMemo, useState } from "react";
import { getZoneDetails, getZoneWithGeometry } from "@/services/backend-rest-client";
import { getCountryNameFromIso3 } from "@/utils/vessel.utils";
import DeckGL, { MapViewState } from "deck.gl";
import { Map as MapGL } from "react-map-gl/maplibre";
import useSWR from "swr";



import { ZoneWithGeometry } from "@/types/zone";
import { convertDurationToString, getDateRange } from "@/libs/dateUtils";
import { useZonesLayer } from "@/components/core/map/layers/use-zones-layer";
import DetailsContainer from "@/components/details/details-container";





export default function AmpDetailsPage({ params }: { params: { id: string } }) {
  const [selectedDays, setSelectedDays] = useState(30)
  const [zone, setZone] = useState<ZoneWithGeometry | null>(null)

  useEffect(() => {
    const fetchZone = async () => {
      const zone = await getZoneWithGeometry(params.id)
      setZone(zone)
      setViewState({
        longitude: zone.centroid.coordinates[0],
        latitude: zone.centroid.coordinates[1],
        zoom: 6,
      })
    }
    if (!zone) {
      fetchZone()
    }
  }, [params.id])

  const { startAt, endAt } = useMemo(() => {
    console.log(selectedDays)
    return getDateRange(selectedDays)
  }, [selectedDays])

  const { data: zoneVisits = [], isLoading } = useSWR(
    [params.id, startAt, endAt],
    () => getZoneDetails(params.id, startAt, endAt).then((res) => res.data),
    {
      revalidateOnMount: true,
      keepPreviousData: true,
    }
  )

  const zoneInfo = useMemo(() => {
    if (!zoneVisits[0]) {
      return null
    }

    const { zone: zoneDetails } = zoneVisits[0]

    return {
      id: zoneDetails.id.toString(),
      label: zoneDetails.name,
      description: zoneDetails.sub_category,
      relatedItemsType: "Vessels",
      relatedItems: zoneVisits.map((visit) => {
        const { vessel, vessel_visiting_time_by_zone } = visit
        return {
          id: vessel.id.toString(),
          title: `${vessel.ship_name} - ${getCountryNameFromIso3(vessel.country_iso3)}`,
          description: `IMO: ${vessel.imo} - MMSI: ${vessel.mmsi} - Type: ${vessel.type} - Length: ${vessel.length} m`,
          value: convertDurationToString(vessel_visiting_time_by_zone),
          type: "vessels",
        }
      }),
    }
  }, [zoneVisits])

  const singleZoneLayer = useZonesLayer({
    zones: zone ? [zone] : [],
    filtersDisabled: true,
  })

  const [viewState, setViewState] = useState<MapViewState>({
    longitude: zone?.centroid.coordinates[0] ?? 0,
    latitude: zone?.centroid.coordinates[1] ?? 0,
    zoom: 5,
  })

  return (
    <div className="h-screen">
      <DetailsContainer
        type="zone"
        details={zoneInfo}
        onDateRangeChange={(value) => {
          setSelectedDays(Number(value))
        }}
        defaultDateRange={"30"}
        isLoading={isLoading}
      >
        {zone && (
          <DeckGL
            viewState={{
              ...viewState,
              longitude: zone.centroid.coordinates[0],
              latitude: zone.centroid.coordinates[1],
            }}
            controller={{
              dragRotate: false,
              touchRotate: false,
              keyboard: false,
              touchZoom: false,
            }}
            layers={singleZoneLayer}
            onViewStateChange={(e) => setViewState(e.viewState as MapViewState)}
          >
            <MapGL
              mapStyle={`https://api.maptiler.com/maps/e9b57486-1b91-47e1-a763-6df391697483/style.json?key=${process.env.NEXT_PUBLIC_MAPTILER_TO}`}
              attributionControl={false}
            ></MapGL>
          </DeckGL>
        )}
      </DetailsContainer>
    </div>
  )
}