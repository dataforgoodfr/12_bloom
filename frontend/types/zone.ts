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
  id: number
  created_at: string
  updated_at: string
  category: string
  sub_category: string
  name: string
}

export interface ZoneMetrics {
  zone: ZoneDetails
  visiting_duration: string
  vessel_visiting_time_by_zone: string
}

export type ZoneVesselMetrics = {
  zone: ZoneDetails
  vessel: VesselDetails
  zone_visiting_time_by_vessel: string
}

export type ZoneWithGeometry = ZoneDetails & {
  geometry: {
    type: string
    coordinates: number[][][]
  }
}
