export type Vessel = {
  name: string
  mmsi: number
  imo: number
  width: number
  length: number
  flag: string
  callsign: string
  ship_type: string | null
}
