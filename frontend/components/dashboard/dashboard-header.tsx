"use client"

import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"
import MapIcon from "@/public/map-icon.svg"
import TrawlWatchLogo from "@/public/trawlwatch.svg"
import { LogOut, Map } from "lucide-react"

import { Button } from "../ui/button"
import PartnerCredits from "../core/map/partner-credits"

export default function DashboardHeader() {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/logout", {
        method: "POST",
      })
      if (response.ok) {
        router.push("/login")
      }
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  return (
    <div className="flex w-full">
      <div className="w-full flex items-center gap-5">
        <Link href="/dashboard">
          <Image
            src={TrawlWatchLogo}
            alt="Trawlwatch logo"
            height={80}
            width={80}
            className="cursor-pointer"
          />
        </Link>
        <PartnerCredits wide={true} />
      </div>

      <Link href="/map">
        <Button
          variant="ghost"
          className="mr-5 flex items-center p-3 hover:cursor-pointer"
        >
          <Map className="text-primary" />
          <div className="inline text-base font-bold text-primary">
            Map&nbsp;view
          </div>
        </Button>
      </Link>
      <Link href="/login" onClick={handleLogout}>
        <Button
          variant="ghost"
          className="flex items-center p-3 hover:cursor-pointer"
        >
          <LogOut className="text-primary" />
          <div className="inline text-base font-bold text-primary">Logout</div>
        </Button>
      </Link>
    </div>
  )
}
