import { Item } from "@/types/item"
import { VesselTrackingTimeDto } from "@/types/vessel"
import { ZoneVisitTimeDto } from "@/types/zone"
import { convertDurationInHours } from "@/libs/dateUtils"

export function convertVesselDtoToItem(
  vesselDtos: VesselTrackingTimeDto[]
): Item[] {
  return vesselDtos?.map((vesselDto: VesselTrackingTimeDto) => {
    return {
      id: `${vesselDto.vessel_id}`,
      title: vesselDto.vessel_ship_name,
      description: `IMO ${vesselDto.vessel_imo} / MMSI ${vesselDto.vessel_mmsi} / ${vesselDto.vessel_length} mètres`,
      value: `${convertDurationInHours(vesselDto.total_time_at_sea)}h`,
      type: "vessel",
    }
  })
}

export function convertZoneDtoToItem(zoneDtos: ZoneVisitTimeDto[]): Item[] {
  return zoneDtos?.map((zoneDto: ZoneVisitTimeDto) => {
    return {
      id: `${zoneDto.zone_id}`,
      title: zoneDto.zone_name,
      description: zoneDto.zone_sub_category,
      value: `${convertDurationInHours(zoneDto.visiting_duration)}h`,
      type: "amp",
    }
  })
}
