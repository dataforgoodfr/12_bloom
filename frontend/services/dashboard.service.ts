import { TOTAL_VESSELS } from "@/constants/totals.constants"
import {
  getTopVesselsInActivity,
  getTopZonesVisited,
  getVesselsTrackedCount,
} from "@/services/backend-rest-client"
import { swrOptions } from "@/services/swr"
import useSWR from "swr"

import { convertVesselDtoToItem, convertZoneDtoToItem } from "@/libs/mapper"

const TOP_ITEMS_SIZE = 5

type DashboardData = {
  topVesselsInActivity: any[]
  topAmpsVisited: any[]
  totalVesselsInActivity: number
  totalAmpsVisited: number
  totalVesselsTracked: number
  isLoading: {
    topVesselsInActivity: boolean
    topAmpsVisited: boolean
    totalVesselsInActivity: boolean
    totalAmpsVisited: boolean
    totalVesselsTracked: boolean
  }
}

export const useDashboardData = (
  startAt: string,
  endAt: string
): DashboardData => {
  const {
    data: topVesselsInActivity = [],
    isLoading: topVesselsInActivityLoading,
  } = useSWR(
    `topVesselsInActivity-${startAt}-${endAt}`,
    async () => {
      try {
        const response = await getTopVesselsInActivity(
          startAt,
          endAt,
          TOP_ITEMS_SIZE
        )
        return convertVesselDtoToItem(response?.data || [])
      } catch (error) {
        console.log(
          "An error occurred while fetching top vessels in activity: " + error
        )
        return []
      }
    },
    swrOptions
  )

  const { data: topAmpsVisited = [], isLoading: topAmpsVisitedLoading } =
    useSWR(
      `topAmpsVisited-${startAt}-${endAt}`,
      async () => {
        try {
          const response = await getTopZonesVisited(
            startAt,
            endAt,
            TOP_ITEMS_SIZE
          )
          return convertZoneDtoToItem(response?.data || [])
        } catch (error) {
          console.log(
            "An error occurred while fetching top amps visited: " + error
          )
          return []
        }
      },
      swrOptions
    )

  const {
    data: totalVesselsInActivity = 0,
    isLoading: totalVesselsInActivityLoading,
  } = useSWR(
    `totalVesselsInActivity-${startAt}-${endAt}`,
    async () => {
      try {
        const response = await getTopVesselsInActivity(startAt, endAt, 1700)
        return response?.data?.length
      } catch (error) {
        console.log(
          "An error occurred while fetching total vessels in activity: " + error
        )
        return 0
      }
    },
    swrOptions
  )

  const { data: totalAmpsVisited = 0, isLoading: totalAmpsVisitedLoading } =
    useSWR(
      `totalAmpsVisited-${startAt}-${endAt}`,
      async () => {
        try {
          const response = await getTopZonesVisited(startAt, endAt, 100000)
          return response?.data?.length
        } catch (error) {
          console.log(
            "An error occurred while fetching total amps visited: " + error
          )
          return 0
        }
      },
      swrOptions
    )

  const {
    data: totalVesselsTracked = TOTAL_VESSELS,
    isLoading: totalVesselsTrackedLoading,
  } = useSWR(
    "vesselsTrackedCount",
    async () => {
      try {
        const response = await getVesselsTrackedCount()
        return response?.data
      } catch (error) {
        console.log(
          "An error occurred while fetching vessels tracked count: " + error
        )
        return TOTAL_VESSELS
      }
    },
    swrOptions
  )

  return {
    topVesselsInActivity,
    topAmpsVisited,
    totalVesselsInActivity,
    totalAmpsVisited,
    totalVesselsTracked,
    isLoading: {
      topVesselsInActivity: topVesselsInActivityLoading,
      topAmpsVisited: topAmpsVisitedLoading,
      totalVesselsInActivity: totalVesselsInActivityLoading,
      totalAmpsVisited: totalAmpsVisitedLoading,
      totalVesselsTracked: totalVesselsTrackedLoading,
    },
  }
}
