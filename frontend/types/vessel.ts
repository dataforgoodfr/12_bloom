export type Vessel = {
  id: number
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

export type VesselTrackingTimeDto = {
  vessel_id: number;
  vessel_mmsi: number;
  vessel_ship_name: string;
  vessel_width: number;
  vessel_length: number;
  vessel_country_iso3: string;
  vessel_type: string;
  vessel_imo: number;
  vessel_cfr: string;
  vessel_external_marking: string;
  vessel_ircs: string;
  vessel_home_port_id: number;
  vessel_details: string;
  vessel_tracking_activated: boolean
  vessel_tracking_status: string;
  vessel_length_class: string;
  vessel_check: string;
  total_time_at_sea: string;
}

export type VesselPositions = VesselPosition[]

export interface VesselPosition {
  arrival_port: string;
  excurision_id: number;
  heading: number;
  position: VesselPositionCoordinates;
  speed: number;
  timestamp: string;
  vessel: Vessel;
}

export interface VesselPositionCoordinates {
  coordinates: number[];
  type: string;
}

export type VesselExcursionSegmentGeo = {
  speed: number
  heading?: number
  navigational_status: string
  geometry: {
    type: string;
    coordinates: number[][];
  } 
}

export type VesselExcursionSegmentsGeo = {
  vesselId: number
  type: any;
  features: any;
}

export type VesselExcursionSegments = {
  vesselId: number;
  segments: VesselExcursionSegment[];
}

export type VesselExcursion = {
    id: number;
    vessel_id: number;
    departure_port_id: number;
    departure_at: string;
    departure_position: {
      coordinates: number[];
    }
    arrival_port_id: number;
    arrival_at: number;
    arrival_position: number;
    excursion_duration: number;
    total_time_at_sea: string;
    total_time_in_amp: string;
    total_time_in_territorial_waters: string;
    total_time_in_costal_waters: string;
    total_time_fishing: string;
    total_time_fishing_in_amp: string;
    total_time_fishing_in_territorial_waters: string;
    total_time_fishing_in_costal_waters: string;
    total_time_extincting_amp: string;
    created_at: string;
    updated_at: String;
}

export type VesselExcursionSegment = {
    id: number;
    vessel_id: number;
    excursion_id: number;
    timestamp_start: string;
    timestamp_end: string;
    segment_duration: string;
    start_position: Position
    end_position: Position;
    course: number;
    distance: number;
    average_speed: number;
    speed_at_start: number;
    speed_at_end: number;
    heading_at_start: number;
    heading_at_end: number;
    type: string;
    in_amp_zone: boolean;
    in_territorial_waters: boolean;
    in_costal_waters: boolean;
    last_vessel_segment: boolean;
    created_at: string;
    updated_at: string;
}

export type Position = {
  type: string;
  coordinates: number[]
}