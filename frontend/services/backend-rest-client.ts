
import { Vessel, VesselExcursion, VesselExcursionSegment, VesselPositions } from "@/types/vessel";
import axios, { InternalAxiosRequestConfig } from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;
const API_KEY = process.env.NEXT_PUBLIC_BACKEND_API_KEY ?? 'no-key-found';

// Authenticate all requests to Bloom backend
axios.interceptors.request.use((request: InternalAxiosRequestConfig) => {
  request.headers.set('x-key', API_KEY);
    return request;
});

export function getVessels() {
  return axios.get<Vessel[]>(`${BASE_URL}/vessels`);
}

export function getVesselsLatestPositions() {
  return axios.get<VesselPositions>(`${BASE_URL}/vessels/all/positions/last`);
}

export function getVesselExcursion(vesselId: number) {
  return axios.get<VesselExcursion[]>(`${BASE_URL}/vessels/${vesselId}/excursions`);
}

export function getVesselSegments(vesselId: number, excursionId: number) {
  return axios.get<VesselExcursionSegment[]>(`${BASE_URL}/vessels/${vesselId}/excursions/${excursionId}/segments`);
}

export async function getVesselFirstExcursionSegments(vesselId: number) {
  const response = await getVesselExcursion(vesselId);
  const excursionId = response?.data[0]?.id;
  return !!excursionId ? getVesselSegments(vesselId, excursionId) : [];
}
