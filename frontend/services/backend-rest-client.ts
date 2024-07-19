
import { Vessel, VesselExcursion, VesselExcursionSegment, VesselPositions } from "@/types/vessel";
import axios from "axios";

const BASE_URL = "http://localhost:8000";

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
