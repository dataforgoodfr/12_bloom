import {
  getTopVesselsInActivity,
  getTopZonesVisited,
} from "@/services/backend-rest-client"

import { format } from "@/libs/dateUtils"
import DashboardHeader from "@/components/dashboard/dashboard-header"
import DashboardOverview from "@/components/dashboard/dashboard-overview"

const DAYS_SINCE_TODAY = 360
const TOP_ITEMS_SIZE = 5

async function fetchTopVesselsInActivity() {
  try {
    let today = new Date()
    let startAt = new Date(
      new Date().setDate(today.getDate() - DAYS_SINCE_TODAY)
    )
    const response = await getTopVesselsInActivity(
      format(startAt),
      format(today),
      TOP_ITEMS_SIZE
    )
    return response?.data
  } catch (error) {
    console.log(
      "An error occured while fetching top vessels in activity : " + error
    )
    return []
  }
}

async function fetchTopAmpsVisited() {
  try {
    let today = new Date()
    let startAt = new Date(
      new Date().setDate(today.getDate() - DAYS_SINCE_TODAY)
    )
    const response = await getTopZonesVisited(
      format(startAt),
      format(today),
      TOP_ITEMS_SIZE
    )
    return response?.data
  } catch (error) {
    console.log("An error occured while fetching top amps visited: " + error)
    return []
  }
}

async function fetchTotalVesselsInActivity() {
  try {
    let today = new Date()
    let startAt = new Date(
      new Date().setDate(today.getDate() - DAYS_SINCE_TODAY)
    )
    // TODO(CT): replace with new endpoint (waiting for Hervé)
    const response = await getTopVesselsInActivity(
      format(startAt),
      format(today),
      10000
    ) // high value to capture all data
    return response?.data?.length
  } catch (error) {
    console.log("An error occured while fetching top amps visited: " + error)
    return 0
  }
}

async function fetchTotalAmpsVisited() {
  try {
    let today = new Date()
    let startAt = new Date(
      new Date().setDate(today.getDate() - DAYS_SINCE_TODAY)
    )
    // TODO(CT): replace with new endpoint (waiting for Hervé)
    const response = await getTopZonesVisited(
      format(startAt),
      format(today),
      10000
    ) // high value to capture all data
    return response?.data?.length
  } catch (error) {
    console.log("An error occured while fetching top amps visited: " + error)
    return 0
  }
}

export default async function DashboardPage() {
  const topVesselsInActivity = await fetchTopVesselsInActivity()
  const topAmpsVisited = await fetchTopAmpsVisited()
  const totalVesselsInActivity = await fetchTotalVesselsInActivity()
  const totalAmpsVisited = await fetchTotalAmpsVisited()

  return (
    <section className="h-svh bg-color-3 px-6">
      <div className="block h-1/6 w-full">
        <DashboardHeader />
      </div>

      <div className="h-5/6 w-full">
        <DashboardOverview
          topVesselsInActivity={topVesselsInActivity}
          topAmpsVisited={topAmpsVisited}
          totalVesselsActive={totalVesselsInActivity}
          totalAmpsVisited={totalAmpsVisited}
        />
      </div>
    </section>
  )
}
