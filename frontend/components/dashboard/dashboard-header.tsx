"use client"

import Image from "next/image"
import { useRouter } from "next/navigation"
import MapIcon from "@/public/map-icon.svg"
import TrawlWatchLogo from "@/public/trawlwatch.svg"

export default function DashboardHeader() {
  const router = useRouter()

  const onClickMapView = () => {
    router.push("/map")
  }

  return (
    <div className="flex w-full pt-5">
      <div className="w-full">
        <Image
          src={TrawlWatchLogo}
          alt="Trawlwatch logo"
          height={80}
          width={80}
        />
      </div>

      <button
        className="flex items-center hover:cursor-pointer"
        onClick={onClickMapView}
      >
        <Image src={MapIcon} alt="Map view" height={30} width={30} />
        <div className="ml-2 mr-5 inline font-bold text-color-1">
          Map&nbsp;view
        </div>
      </button>
    </div>
  )
}
