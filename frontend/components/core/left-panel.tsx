"use client"

import { useEffect, useState } from "react"
import Image from "next/image"
import TrawlWatchLogo from "@/public/trawlwatch.svg"
import { ChartBarIcon } from "@heroicons/react/24/outline"
import { motion, useAnimationControls } from "framer-motion"

import NavigationLink from "@/components/ui/navigation-link"
import { VesselFinderDemo } from "@/components/core/command/vessel-finder"

import Spinner from "../ui/custom/spinner"
import TrackedVesselsPanel from "./tracked-vessel/tracked-vessels-panel"
import { ChevronRightIcon } from "lucide-react"
import { useMapStore } from "@/libs/stores/map-store"
import { useShallow } from "zustand/react/shallow"

const containerVariants = {
  close: {
    width: "5rem",
    transition: {
      type: "spring",
      damping: 15,
      duration: 0.5,
    },
  },
  open: {
    width: "24rem",
    transition: {
      type: "spring",
      damping: 15,
      duration: 0.3,
    },
  },
}

const svgVariants = {
  close: {
    rotate: 360,
  },
  open: {
    rotate: 180,
  },
}

type LeftPanelProps = {
  isLoading: boolean
}

export default function LeftPanel({ isLoading }: LeftPanelProps) {
  const [isOpen, setIsOpen] = useState(false)
  const containerControls = useAnimationControls()
  const svgControls = useAnimationControls()

  const { mode: mapMode } = useMapStore(useShallow((state) => ({
    mode: state.mode,
  })))

  useEffect(() => {
    const control = isOpen ? "open" : "close"
    containerControls.start(control)
    svgControls.start(control)
  }, [containerControls, isOpen, svgControls])

  const handleOpenClose = () => {
    setIsOpen(!isOpen)
  }

  return (
    <>
      <motion.nav
        variants={containerVariants}
        animate={containerControls}
        initial="close"
        className="absolute left-0 top-0 z-10 flex max-h-screen flex-col gap-3 rounded-br-lg bg-color-3 shadow shadow-color-2"
      >
        <div className="flex w-full flex-row place-items-center justify-between p-5">
          <Image
              src={TrawlWatchLogo}
              alt="Trawlwatch logo"
              height={80}
              width={80}
            />
          <div className="absolute right-0 top-0 translate-x-3/4 bg-color-3 rounded-lg h-16 flex items-center justify-right px-1">
            <button
              className="ml-3 flex rounded-full p-1"
              onClick={() => handleOpenClose()}
            >
              <motion.div
                animate={svgControls}
                variants={svgVariants}
                initial="close"
              >
                <ChevronRightIcon className="size-8" />
              </motion.div>
            </button>
          </div>
        </div>
        {mapMode === "position" && (
          <>
            <div className="flex flex-col gap-3 p-5">
              <NavigationLink href="/dashboard" name="Dashboard" wide={isOpen}>
                <ChartBarIcon className="w-8 min-w-8 stroke-inherit stroke-[0.75]" />
            </NavigationLink>
          </div>
          <div className="flex flex-col gap-3 bg-color-3 p-5">
              {isLoading ? <Spinner /> : <VesselFinderDemo wideMode={isOpen} />}
            </div>
          </>
        )}
        <div
          className={`flex flex-col gap-3 overflow-auto bg-color-2 p-5 ${isOpen ? "cursor-default" : "cursor-pointer"}`}
          onClick={() => !isOpen && setIsOpen(true)}
        >
          <TrackedVesselsPanel
            wideMode={isOpen}
          />
        </div>
      </motion.nav>
    </>
  )
}
