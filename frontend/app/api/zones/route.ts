import { NextResponse } from "next/server"
import { getZones } from "@/services/backend-rest-client"

export async function GET() {
  try {
    const response = await getZones()
    return NextResponse.json(response?.data)
  } catch (error) {
    console.error("Error fetching zones:", error)
    return NextResponse.json([], { status: 500 })
  }
}
