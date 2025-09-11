import { VesselDetails } from "./vessel"

export enum ZoneCategory {
  AMP = "amp",
  FISHING_COASTAL_WATERS = "Fishing coastal waters (6-12 NM)",
  TERRITORIAL_SEAS = "Territorial seas",
}

export type ZoneVisitTimeDto = {
  zone_id: number
  zone_category: string
  zone_sub_category: string
  zone_name: string
  visiting_duration: string
}

export interface ZoneDetails {
  id: string
  created_at: string
  updated_at: string
  category: string
  sub_category: string
  name: string
  centroid: {
    type: "Point"
    coordinates: number[]
  }
}

export interface ZoneMetrics {
  zone: ZoneDetails
  total_visit_duration: string
}

export type ZoneVesselMetrics = {
  zone: ZoneDetails
  vessel: VesselDetails
  vessel_visiting_time_by_zone: string
}

export type VesselZoneMetrics = {
  vessel: VesselDetails
  zone: ZoneDetails
  vessel_visiting_time_by_zone: string
}

export type ZoneWithGeometry = ZoneDetails & {
  geometry: {
    type: string
    coordinates: GeoJSON.Position[][][]
  }
}
