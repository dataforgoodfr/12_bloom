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

export type VesselVoyageTracksPropertiesType = {
  vessel_ais_class: string
  vessel_flag: string
  vessel_name: string
  vessel_callsign: string
  vessel_ship_type?: string
  vessel_sub_ship_type?: string
  vessel_mmsi: number
  vessel_imo: number
  vessel_width: number
  vessel_length: number
  voyage_destination?: string
  voyage_draught?: number
  voyage_eta: string
}

export type VesselTrailPropertiesType = {
  vessel_mmsi: number
  speed: number
  heading?: number
  navigational_status: string
}