import { NextResponse } from "next/server"
import { getVesselsLatestPositions } from "@/services/backend-rest-client"

export const revalidate = 0 // Don't cache last positions

export async function GET() {
  try {
    const response = await getVesselsLatestPositions()
    return NextResponse.json(response?.data)
  } catch (error) {
    console.error(
      "An error occurred while fetching vessels latest positions:",
      error
    )
    return NextResponse.json([], { status: 500 })
  }
}
