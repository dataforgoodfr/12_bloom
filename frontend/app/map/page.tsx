import {
  getVessels,
  getVesselsLatestPositions,
  getZones,
} from "@/services/backend-rest-client"

import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import Map from "@/components/core/map/main-map"
import PositionPreview from "@/components/core/map/position-preview"

export const revalidate = 900

async function fetchVessels() {
  try {
    const response = await getVessels()
    return response?.data
  } catch (error) {
    console.log("An error occured while fetching vessels: " + error)
    return []
  }
}

// TODO(CT): move this logic within a cron job
async function fetchLatestPositions() {
  try {
    const response = await getVesselsLatestPositions()
    return response?.data
  } catch (error) {
    console.log(
      "An error occured while fetching vessels latest positions: " + error
    )
    return []
  }
}

async function fetchZones() {
  const response = await getZones()
  return response?.data
}

export default async function MapPage() {
  const [vessels, latestPositions, zones] = await Promise.all([
    fetchVessels(),
    fetchLatestPositions(),
    fetchZones(),
  ])

  return (
    <>
      <LeftPanel vessels={vessels} />
      <Map vesselsPositions={latestPositions} zones={zones} />
      <MapControls />
      <PositionPreview />
    </>
  )
}
