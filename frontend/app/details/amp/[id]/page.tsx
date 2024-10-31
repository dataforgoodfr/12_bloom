import DetailsContainer from "@/components/details/details-container"

export default async function AmpDetailsPage({
  params,
}: {
  params: { id: string }
}) {
  // const ampDetails = await getAmpDetails(params.id)

  return <DetailsContainer details={null} />
}
