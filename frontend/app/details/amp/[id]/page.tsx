import mockData from "@/mock-data-details.json"

import DetailsContainer from "@/components/details/details-container"

export default function AmpDetailsPage() {
  const ampDetails = mockData["ampDetails"]

  return <DetailsContainer details={ampDetails} />
}
