import mockData from "@/public/data/mock-data-details.json"

import DetailsContainer from "@/components/details/details-container"

export default function VesselDetailsPage() {
  const vesselDetails = mockData["vesselDetails"]

  return <DetailsContainer details={vesselDetails} />
}
