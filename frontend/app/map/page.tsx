import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import DemoMap from "@/components/core/map/main-map"
import PositionPreview from "@/components/core/map/position-preview"
import { getVessels, getVesselsLatestPositions } from "@/services/backend-rest-client"

async function fetchVessels() {
  try {
      const response = await getVessels();
      return response?.data;

    } catch(error) {
      console.log("An error occured while fetching vessels: " + error)
      return [];
    }
}

// TODO(CT): move this logic within a cron job
async function fetchLatestPositions() {
  try {
    const response = await getVesselsLatestPositions();
    return response?.data;
    
  } catch(error) {
    console.log("An error occured while fetching vessels latest positions: " + error)
    return [];
  }
}
  
export default async function MapPage() {
  const vessels = await fetchVessels();
  const latestPositions = await fetchLatestPositions();

  // TODO: create new client component dedicated to update store 
  // -> then Map + LeftPanel can just use storeProvider
  return (
    <>
      <LeftPanel vessels={vessels} />
      <DemoMap vesselsPositions={latestPositions} />
      <MapControls />
      <PositionPreview />
    </>
  )
}
