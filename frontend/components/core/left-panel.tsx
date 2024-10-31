"use client"

import { useEffect, useState } from "react"
import Image from "next/image"
import TrawlWatchLogo from "@/public/trawlwatch.svg"
import { ChartBarIcon } from "@heroicons/react/24/outline"
import { motion, useAnimationControls } from "framer-motion"

import { Vessel } from "@/types/vessel"
import NavigationLink from "@/components/ui/navigation-link"
import { VesselFinderDemo } from "@/components/core/command/vessel-finder"
import { useVesselsStore } from "@/components/providers/vessels-store-provider"

import TrackedVesselsPanel from "./tracked-vessels-panel"

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
    width: "16rem",
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
  vessels: Vessel[]
}

export default function LeftPanel({ vessels }: LeftPanelProps) {
  const [isOpen, setIsOpen] = useState(false)
  const containerControls = useAnimationControls()
  const svgControls = useAnimationControls()
  const { setVessels } = useVesselsStore((state) => state)

  useEffect(() => {
    setVessels(vessels)
  }, [setVessels, vessels])

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
          {!!isOpen && (
            <Image
              src={TrawlWatchLogo}
              alt="Trawlwatch logo"
              height={80}
              width={80}
            />
          )}
          <button
            className="ml-3 flex rounded-full p-1"
            onClick={() => handleOpenClose()}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1}
              stroke="currentColor"
              className="size-6 stroke-neutral-200"
            >
              <motion.path
                strokeLinecap="round"
                strokeLinejoin="round"
                variants={svgVariants}
                animate={svgControls}
                d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                transition={{
                  duration: 0.5,
                  ease: "easeInOut",
                }}
              />
            </svg>
          </button>
        </div>
        <div className="flex flex-col gap-3 p-5">
          <NavigationLink href="/dashboard" name="Dashboard" wide={isOpen}>
            <ChartBarIcon className="w-8 min-w-8 stroke-inherit stroke-[0.75]" />
          </NavigationLink>
        </div>
        <div className="flex flex-col gap-3 bg-color-3 p-5">
          <VesselFinderDemo wideMode={isOpen} />
        </div>
        <div className="flex flex-col gap-3 overflow-auto bg-color-3 p-5">
          <TrackedVesselsPanel
            wideMode={isOpen}
            parentIsOpen={isOpen}
            openParent={() => setIsOpen(true)}
          />
        </div>
      </motion.nav>
    </>
  )
}
