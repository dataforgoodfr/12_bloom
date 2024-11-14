export type ZoneVisitTimeDto = {
  zone_id: number
  zone_category: string
  zone_sub_category: string
  zone_name: string
  visiting_duration: string
}

export interface ZoneVisits {
  zone_id: number
  zone_category: string
  zone_sub_category: string
  zone_name: string
  vessel_id: number
  vessel_name: string
  vessel_type: string
  vessel_length_class: string
  zone_visiting_time_by_vessel: string // ISO 8601 duration format
}
