import { NextResponse } from "next/server"
import { getVessels } from "@/services/backend-rest-client"

export async function GET() {
  try {
    const response = await getVessels()
    return NextResponse.json(response?.data)
  } catch (error) {
    console.error("An error occurred while fetching vessels:", error)
    return NextResponse.json([], { status: 500 })
  }
}
