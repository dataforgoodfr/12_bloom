import { Item } from "@/types/item"
import { VesselMetrics } from "@/types/vessel"
import { ZoneMetrics } from "@/types/zone"
import { convertDurationInHoursStr } from "@/libs/dateUtils"

export function convertVesselDtoToItem(metrics: VesselMetrics[]): Item[] {
  return metrics
    ?.map((vesselMetrics) => {
      const vessel = vesselMetrics.vessel
      return {
        id: `${vessel.id}`,
        title: vessel.ship_name,
        description: `IMO ${vessel.imo} / MMSI ${vessel.mmsi} / ${vessel.length} m`,
        value: `${convertDurationInHoursStr(vesselMetrics.total_time_at_sea)}h`,
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
    const { zone, visiting_duration } = zoneMetrics
    return {
      id: `${zone.id}`,
      title: zone.name,
      description: zone.sub_category,
      value: `${convertDurationInHoursStr(visiting_duration)}h`,
      type: "amp",
    }
  })
}
