import { Item } from "@/types/item"
import { VesselMetrics } from "@/types/vessel"
import { ZoneMetrics } from "@/types/zone"
import { convertDurationToString } from "@/libs/dateUtils"

export function convertVesselDtoToItem(metrics: VesselMetrics[]): Item[] {
  return metrics
    ?.map((vesselMetrics) => {
      const vessel = vesselMetrics.vessel
      return {
        id: `${vessel.id}`,
        title: vessel.ship_name,
        description: `IMO ${vessel.imo} / MMSI ${vessel.mmsi} / ${vessel.length} m`,
        value: convertDurationToString(vesselMetrics.total_time_in_category),
        type: "vessel",
        countryIso3: vessel.country_iso3,
      }
    })
    .sort((a, b) => {
      return Number(b.value.split("h")[0]) - Number(a.value.split("h")[0])
    })
}

export function convertZoneDtoToItem(zoneMetrics: ZoneMetrics[]): Item[] {
  return zoneMetrics?.map((zoneMetrics) => {
    const { zone, total_visit_duration } = zoneMetrics
    return {
      id: `${zone.id}`,
      title: zone.name,
      description: zone.sub_category,
      value: convertDurationToString(total_visit_duration),
      type: "amp",
    }
  })
}
