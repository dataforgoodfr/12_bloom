"use client"

import { useEffect, useState } from "react"
import Image from "next/image"
import TrawlWatchLogo from "@/public/trawlwatch.svg"
import { ChartBarIcon } from "@heroicons/react/24/outline"
import { motion, useAnimationControls } from "framer-motion"
import { ChevronRightIcon } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import { useLoaderStore } from "@/libs/stores/loader-store"
import { useMapStore } from "@/libs/stores/map-store"
import NavigationLink from "@/components/ui/navigation-link"
import { VesselFinderDemo } from "@/components/core/command/vessel-finder"

import Spinner from "../ui/custom/spinner"
import TrackedVesselsPanel from "./tracked-vessel/tracked-vessels-panel"

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

export default function LeftPanel() {
  const containerControls = useAnimationControls()
  const svgControls = useAnimationControls()

  const { vesselsLoading } = useLoaderStore(
    useShallow((state) => ({
      vesselsLoading: state.vesselsLoading,
    }))
  )

  const {
    mode: mapMode,
    leftPanelOpened,
    setLeftPanelOpened,
  } = useMapStore(
    useShallow((state) => ({
      mode: state.mode,
      leftPanelOpened: state.leftPanelOpened,
      setLeftPanelOpened: state.setLeftPanelOpened,
    }))
  )

  useEffect(() => {
    const control = leftPanelOpened ? "open" : "close"
    containerControls.start(control)
    svgControls.start(control)
  }, [containerControls, leftPanelOpened, svgControls])

  const handleOpenClose = () => {
    setLeftPanelOpened(!leftPanelOpened)
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
          <div className="justify-right absolute right-0 top-0 flex h-16 translate-x-3/4 items-center rounded-lg bg-color-3 px-1">
            <button
              className="ml-3 flex rounded-full p-1"
              onClick={() => handleOpenClose()}
            >
              <motion.div
                animate={svgControls}
                variants={svgVariants}
                initial="close"
              >
                <ChevronRightIcon className="size-8 text-neutral-200" />
              </motion.div>
            </button>
          </div>
        </div>
        {mapMode === "position" && (
          <>
            <div className="flex flex-col gap-3 p-5">
              <NavigationLink
                href="/dashboard"
                name="Dashboard"
                wide={leftPanelOpened}
              >
                <ChartBarIcon className="w-8 min-w-8 stroke-neutral-200 stroke-1 hover:stroke-[1.25]" />
              </NavigationLink>
            </div>
            <div className="flex flex-col gap-3 bg-color-3 p-5">
              {vesselsLoading ? (
                <div className="flex items-center justify-center">
                  <Spinner className="text-white" />
                </div>
              ) : (
                <VesselFinderDemo wideMode={leftPanelOpened} />
              )}
            </div>
          </>
        )}
        <div
          className={`flex flex-col gap-3 overflow-auto bg-color-2 p-5 ${leftPanelOpened ? "cursor-default" : "cursor-pointer"}`}
          onClick={() => !leftPanelOpened && setLeftPanelOpened(true)}
        >
          <TrackedVesselsPanel wideMode={leftPanelOpened} />
        </div>
      </motion.nav>
    </>
  )
}
