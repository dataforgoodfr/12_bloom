import { Item } from "@/types/item";
import { VesselTrackingTimeDto } from "@/types/vessel";
import { ZoneVisitTimeDto } from "@/types/zone";

export function convertVesselDtoToItem(vesselDtos: VesselTrackingTimeDto[]): Item[] {
  return vesselDtos?.map((vesselDto: VesselTrackingTimeDto) => {
    return {
      id: `${vesselDto.vessel_id}`,
      title: vesselDto.vessel_ship_name,
      description: `IMO ${vesselDto.vessel_imo} / MMSI ${vesselDto.vessel_mmsi} / ${vesselDto.vessel_length} mètres`,
      value: vesselDto.total_time_at_sea,
      type: "vessel"
    }
  });
}

export function convertZoneDtoToItem(zoneDtos: ZoneVisitTimeDto[]): Item[] {
  return zoneDtos?.map((zoneDto: ZoneVisitTimeDto) => {
    return {
      id: `${zoneDto.zone_id}`,
      title: zoneDto.zone_name,
      description: zoneDto.zone_sub_category,
      value: zoneDto.visiting_duration,
      type: "amp"
    }
  })
}