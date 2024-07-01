import mockData from "@/public/data/mock-data-details.json"

import DetailsContainer from "@/components/details/details-container"

export default function AmpDetailsPage() {
  const ampDetails = mockData["ampDetails"]

  return <DetailsContainer details={ampDetails} />
}
