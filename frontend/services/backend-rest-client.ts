import { TOTAL_AMPS } from "@/constants/totals.constants"
import axios, { InternalAxiosRequestConfig } from "axios"

import { Port } from "@/types/port"
import {
  Vessel,
  VesselDetails,
  VesselExcursion,
  VesselExcursionSegment,
  VesselExcursionSummary,
  VesselExcursionTimeByZone,
  VesselMetrics,
  VesselPositions,
} from "@/types/vessel"
import {
  VesselZoneMetrics,
  ZoneMetrics,
  ZoneVesselMetrics,
  ZoneWithGeometry,
} from "@/types/zone"

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL
const API_KEY = process.env.NEXT_PUBLIC_BACKEND_API_KEY ?? "no-key-found"
const CACHE_CONTROL_HEADER = "public, max-age=2592000" // 30 days in seconds

// Authenticate all requests to Bloom backend
axios.interceptors.request.use((request: InternalAxiosRequestConfig) => {
  request.headers.set("x-key", API_KEY)
  return request
})

export function getVessels() {
  const url = `${BASE_URL}/vessels`
  console.log(`GET ${url}`)
  return axios.get<Vessel[]>(url)
}

export function getVesselsAtSea(startAt: string, endAt: string) {
  const url = `${BASE_URL}/metrics/vessels-at-sea?start_at=${startAt}&end_at=${endAt}`
  console.log(`GET ${url}`)
  return axios.get<number>(url)
}

export function getVesselsTrackedCount() {
  const url = `${BASE_URL}/vessels/tracked-count`
  console.log(`GET ${url}`)
  return axios.get<number>(url)
}

export function getVesselsLatestPositions() {
  const url = `${BASE_URL}/vessels/all/positions/last`
  console.log(`GET ${url}`)
  return axios.get<VesselPositions>(url)
}

export function getVesselClasses() {
  const url = `${BASE_URL}/vessels/classes`
  console.log(`GET ${url}`)
  return axios.get<string[]>(url, {
    headers: { "Cache-Control": CACHE_CONTROL_HEADER },
  })
}

export function getVesselTypes() {
  const url = `${BASE_URL}/vessels/types`
  console.log(`GET ${url}`)
  return axios.get<string[]>(url, {
    headers: { "Cache-Control": CACHE_CONTROL_HEADER },
  })
}

export function getCountries() {
  const url = `${BASE_URL}/vessels/countries`
  console.log(`GET ${url}`)
  return axios.get<string[]>(url, {
    headers: { "Cache-Control": CACHE_CONTROL_HEADER },
  })
}

export function getVesselExcursions(
  vesselId: string,
  startDate?: Date,
  endDate?: Date
) {
  let queryParams: string[] = []
  if (startDate) {
    queryParams.push(`start_at=${startDate.toISOString()}`)
  }
  if (endDate) {
    queryParams.push(`end_at=${endDate.toISOString()}`)
  }
  const url = `${BASE_URL}/vessels/${vesselId}/excursions${queryParams.length > 0 ? `?${queryParams.join("&")}` : ""}`
  console.log(`GET ${url}`)
  return axios.get<VesselExcursion[]>(url)
}

export function getVesselExcursionsExtracts(
  vesselId: string,
  startDate?: Date,
  endDate?: Date
) {
  let queryParams: string[] = []
  if (startDate) {
    queryParams.push(`start_at=${startDate.toISOString()}`)
  }
  if (endDate) {
    queryParams.push(`end_at=${endDate.toISOString()}`)
  }
  const url = `${BASE_URL}/vessels/${vesselId}/excursions${queryParams.length > 0 ? `?${queryParams.join("&")}` : ""}`
  console.log(`GET ${url}`)
  return axios.get<VesselExcursionSummary>(url)
}

export function getVesselSegments(vesselId: string, excursionId: string) {
  const url = `${BASE_URL}/vessels/${vesselId}/excursions/${excursionId}/segments`
  console.log(`GET ${url}`)
  return axios.get<VesselExcursionSegment[]>(url)
}

export async function getVesselFirstExcursionSegments(vesselId: string) {
  try {
    const response = await getVesselExcursions(vesselId)
    const excursionId = response?.data[0]?.excursion_id
    if (!!excursionId) {
      const segments = await getVesselSegments(vesselId, excursionId)
      return segments.data
    }
    return []
  } catch (error) {
    console.error(error)
    return []
  }
}

export function getTopVesselsInActivity(
  startAt: string,
  endAt: string,
  topVesselsLimit: number
) {
  const url = `${BASE_URL}/metrics/vessels/activity?start_at=${startAt}&end_at=${endAt}&limit=${topVesselsLimit}&order=DESC&category=amp`
  console.log(`GET ${url}`)
  return axios.get<VesselMetrics[]>(url)
}

export function getTopZonesVisited(
  startAt: string,
  endAt: string,
  topZonesLimit: number,
  category?: string
) {
  const url = `${BASE_URL}/metrics/zones/activity?${
    category ? `category=${category}&` : ""
  }start_at=${startAt}&end_at=${endAt}&limit=${topZonesLimit}&order=DESC`
  console.log(`GET ${url}`)
  return axios.get<ZoneMetrics[]>(url)
}

export function getVisitedMPAsNumber(
  startAt: string,
  endAt: string,
) {
  const url = `${BASE_URL}/metrics/mpas-visited?start_at=${startAt}&end_at=${endAt}`
  console.log(`GET ${url}`)
  return axios.get<number>(url)
}


export function getTimeByZone(
  startAt: string,
  endAt: string,
  topZonesLimit: number,
  category?: string,
  vesselId?: string
) {
  const url = `${BASE_URL}/metrics/vessels/time-by-zone?${
    category ? `category=${category}&` : ""
  }${vesselId ? `vessel_id=${vesselId}&` : ""}start_at=${startAt}&end_at=${endAt}&limit=${topZonesLimit}&order=DESC`
  console.log(`GET ${url}`)
  return axios.get<VesselZoneMetrics[]>(url)
}

export async function getZoneDetails(
  zoneId: string,
  startAt: string,
  endAt: string
) {
  const url = `${BASE_URL}/metrics/zones/${zoneId}/visiting-time-by-vessel?start_at=${startAt}&end_at=${endAt}&order=DESC&limit=10`
  console.log(`GET ${url}`)
  const response = await axios.get<ZoneVesselMetrics[]>(url)
  return response
}

export async function getZones() {
  const url = `${BASE_URL}/zones`
  console.log(`GET ${url}`)

  // Calculate ranges for batches of 10
  const ranges = []
  for (let i = 0; i < TOTAL_AMPS; i += 100) {
    const end = Math.min(i + 99, TOTAL_AMPS - 1)
    ranges.push(`items=${i}-${end}`)
  }

  // Add start time
  const startTime = performance.now()

  // Make parallel requests for each range
  const responses = await Promise.all(
    ranges.map((range) =>
      axios.get<ZoneWithGeometry[]>(url, {
        headers: { range, "Cache-Control": CACHE_CONTROL_HEADER },
      })
    )
  )

  // Calculate and log duration
  const duration = performance.now() - startTime
  console.log(`Fetched zones in ${(duration / 1000).toFixed(2)}s`)

  // Combine all responses
  return {
    data: responses.flatMap((response) => response.data),
  }
}

export async function getZoneWithGeometry(zoneId: string) {
  const url = `${BASE_URL}/zones/${zoneId}`
  console.log(`GET ${url}`)

  const response = await axios.get<ZoneWithGeometry>(url, {
    headers: { "Cache-Control": CACHE_CONTROL_HEADER },
  })
  return response.data
}

export async function getVesselTimeByZone({
  vesselId,
  category,
  startAt,
  endAt,
}: {
  vesselId: string
  category?: string
  startAt?: Date
  endAt?: Date
}): Promise<VesselExcursionTimeByZone[]> {
  const queryParams = [`vessel_id=${vesselId}`]
  if (category) {
    queryParams.push(`category=${category}`)
  }
  if (startAt) {
    queryParams.push(`start_at=${startAt.toISOString()}`)
  }
  if (endAt) {
    queryParams.push(`end_at=${endAt.toISOString()}`)
  }
  const url = `${BASE_URL}/metrics/vessels/time-by-zone?${queryParams.join("&")}`
  const response = await axios.get<VesselExcursionTimeByZone[]>(url)
  return response.data
}

export function getPorts() {
  const url = `${BASE_URL}/ports`
  console.log(`GET ${url}`)
  return axios.get<Port[]>(url)
}
