import { TOTAL_AMPS } from "@/constants/totals.constants"
import axios, { InternalAxiosRequestConfig } from "axios"

import {
  Vessel,
  VesselExcursion,
  VesselExcursionSegment,
  VesselMetrics,
  VesselPositions,
} from "@/types/vessel"
import { ZoneMetrics, ZoneVesselMetrics, ZoneWithGeometry } from "@/types/zone"

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL
const API_KEY = process.env.NEXT_PUBLIC_BACKEND_API_KEY ?? "no-key-found"

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

export function getVesselsLatestPositions() {
  const url = `${BASE_URL}/vessels/all/positions/last`
  console.log(`GET ${url}`)
  return axios.get<VesselPositions>(url)
}

export function getVesselExcursion(vesselId: number) {
  const url = `${BASE_URL}/vessels/${vesselId}/excursions`
  console.log(`GET ${url}`)
  return axios.get<VesselExcursion[]>(url)
}

export function getVesselSegments(vesselId: number, excursionId: number) {
  const url = `${BASE_URL}/vessels/${vesselId}/excursions/${excursionId}/segments`
  console.log(`GET ${url}`)
  return axios.get<VesselExcursionSegment[]>(url)
}

export async function getVesselFirstExcursionSegments(vesselId: number) {
  try {
    const response = await getVesselExcursion(vesselId)
    const excursionId = response?.data[0]?.id
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
  const url = `${BASE_URL}/metrics/vessels-in-activity?start_at=${startAt}&end_at=${endAt}&limit=${topVesselsLimit}&order=DESC`
  console.log(`GET ${url}`)
  return axios.get<VesselMetrics[]>(url)
}

export function getTopZonesVisited(
  startAt: string,
  endAt: string,
  topZonesLimit: number
) {
  const url = `${BASE_URL}/metrics/zone-visited?start_at=${startAt}&end_at=${endAt}&limit=${topZonesLimit}&order=DESC`
  console.log(`GET ${url}`)
  return axios.get<ZoneMetrics[]>(url)
}

export async function getZoneDetails(
  zoneId: string,
  startAt: string,
  endAt: string
) {
  const url = `${BASE_URL}/metrics/zones/${zoneId}/visiting-time-by-vessel?start_at=${startAt}&end_at=${endAt}&order=DESC&limit=10`
  console.log(`GET ${url}`)
  const response = await axios.get<ZoneVesselMetrics[]>(url)
  console.log(response)
  return response
}

export async function getZones() {
  const url = `${BASE_URL}/zones`
  console.log(`GET ${url}`)

  // Calculate ranges for batches of 10
  const ranges = []
  for (let i = 0; i < TOTAL_AMPS; i += 10) {
    const end = Math.min(i + 9, TOTAL_AMPS - 1)
    ranges.push(`items=${i}-${end}`)
  }

  // Make parallel requests for each range
  const responses = await Promise.all(
    ranges.map((range) =>
      axios.get<ZoneWithGeometry[]>(url, {
        headers: { range },
      })
    )
  )

  // Combine all responses
  return {
    data: responses.flatMap((response) => response.data),
  }
}
