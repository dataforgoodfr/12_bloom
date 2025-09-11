import type { Feature, Geometry } from "geojson"

import { ZoneDetails } from "./zone"

export type Vessel = {
  id: string
  mmsi: number
  ship_name: string
  width: number
  length: number
  country_iso3: string
  type: string | null
  imo: number | null
  cfr: string
  external_marking: string
  ircs: string
  length_class: string
}

export type VesselMetrics = {
  vessel: VesselDetails
  total_time_in_category: string
}

export type VesselDetails = {
  id: string
  imo: number
  mmsi: number
  ship_name: string
  width: number | null
  length: number
  country_iso3: string
  type: string
  external_marking: string
  ircs: string
  tracking_activated: boolean
  tracking_status: string
  created_at: string
  updated_at: string | null
  check: string
  length_class: string
}

export type VesselPositions = VesselPosition[]

export interface VesselPosition {
  arrival_port: string
  excursion_id: number
  heading: number
  position: VesselPositionCoordinates
  speed: number
  timestamp: string
  vessel: Vessel
}

export interface SegmentVesselPosition {
  type: "segmentPosition"
  vessel_id: string
  timestamp: string
  position: number[]
  heading?: number
  speed?: number
}

export interface VesselPositionCoordinates {
  coordinates: number[]
  type: string
}

export type VesselExcursionSegmentGeo = {
  vessel_id: string
  excursion_id: string
  speed: number
  navigational_status: string
  type: VesselExcursionSegment["segment_type"]
}

export type VesselExcursionSegmentsGeo = {
  type: "FeatureCollection"
  features: Feature<Geometry, VesselExcursionSegmentGeo>[]
}

export type VesselExcursionSegments = {
  segments: VesselExcursionSegment[]
}

export type VesselExcursionTimeByZone = {
  zone: ZoneDetails
  vessel: VesselDetails
  vessel_visiting_time_by_zone: string
}

export type VesselExcursion = {
  excursion_id: string
  vessel_id: string
  departure_port_id: number
  departure_at: string
  departure_position?: {
    type: "Point"
    coordinates: number[]
  }
  arrival_port_id: number | null
  arrival_at: string | null
  arrival_position?: {
    type: "Point"
    coordinates: number[]
  } | null
  excursion_duration: string
  total_time_at_sea: string
  total_time_in_amp: string
  total_time_in_territorial_waters: string
  total_time_in_zones_with_no_fishing_rights: string

  total_time_fishing: string
  total_time_fishing_in_amp: string
  total_time_fishing_in_territorial_waters: string
  total_time_fishing_in_zones_with_no_fishing_rights: string

  total_time_default_ais: string

  created_at: string
  updated_at: String

  segments?: VesselExcursionSegment[]
  timeByMPAZone?: VesselExcursionTimeByZone[]
}

export type VesselExcursionSummary = {
  vessel_id: string
  total_time_at_sea: string
  total_time_in_amp: string
  total_time_in_territorial_waters: string
  total_time_in_zones_with_no_fishing_rights: string
  total_time_fishing: string
  total_time_fishing_in_amp: string
  total_time_fishing_in_territorial_waters: string
  total_time_fishing_in_zones_with_no_fishing_rights: string
  total_time_default_ais: string

  excursions : VesselExcursion[]

  count: number
}

export interface ExcursionMetrics {
  totalTimeAtSea: number
  mpa: number
  frenchTerritorialWaters: number
  zonesWithNoFishingRights: number
  aisDefault: number
}

export type VesselExcursionSegment = {
  vessel_id: string
  excursion_id: string
  timestamp_start: string
  timestamp_end: string
  segment_duration: string
  start_position: Position
  end_position: Position
  course_at_start: number
  course_at_end: number
  average_speed: number
  speed_at_start: number
  speed_at_end: number
  heading_at_start: number
  heading_at_end: number
  segment_type: "AT_SEA" | "FISHING" | "DEFAULT_AIS"
  in_amp_zone: boolean
  in_territorial_waters: boolean
  in_zones_with_no_fishing_rights: boolean
  created_at: string
}


export type Position = {
  type: string
  coordinates: number[]
}
