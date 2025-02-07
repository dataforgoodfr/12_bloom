import { NextResponse } from "next/server"
import { getVesselsLatestPositions } from "@/services/backend-rest-client"

export async function GET() {
  try {
    const response = await getVesselsLatestPositions()
    console.log(response.data)
    return NextResponse.json(response?.data)
  } catch (error) {
    console.error(
      "An error occurred while fetching vessels latest positions:",
      error
    )
    return NextResponse.json([], { status: 500 })
  }
}
