"use client"

import { useEffect, useState } from "react"
import Image from "next/image"
import TrawlWatchLogo from "@/public/trawlwatch.svg"
import {
  ChartBarIcon,
  ChartPieIcon,
  DocumentCheckIcon,
  MagnifyingGlassIcon,
  Square2StackIcon,
  UsersIcon,
} from "@heroicons/react/24/outline"
import { AnimatePresence, motion, useAnimationControls } from "framer-motion"
import { Ship as ShipIcon } from "lucide-react"

import NavigationLink from "@/components/ui/navigation-link"
import { useMapStore } from "@/components/providers/map-store-provider"

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
      duration: 0.5,
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

const LeftPanel = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<string | null>(null)

  const containerControls = useAnimationControls()
  const svgControls = useAnimationControls()

  useEffect(() => {
    if (isOpen) {
      containerControls.start("open")
      svgControls.start("open")
    } else {
      containerControls.start("close")
      svgControls.start("close")
    }
  }, [isOpen])

  const handleOpenClose = () => {
    setIsOpen(!isOpen)
    setSelectedProject(null)
  }

  return (
    <>
      <motion.nav
        variants={containerVariants}
        animate={containerControls}
        initial="close"
        className="absolute left-0 top-0 z-10 flex flex-col gap-3 overflow-auto rounded-br-lg bg-slate-800 shadow shadow-slate-600"
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
        <div className="flex flex-col gap-3 bg-slate-800 p-5">
          <NavigationLink href="#" name="Find vesssels" wide={isOpen}>
            <MagnifyingGlassIcon className="w-8 min-w-8 stroke-inherit stroke-[0.75]" />
          </NavigationLink>
        </div>
        <div className="flex flex-col gap-3 bg-slate-600 p-5">
          <NavigationLink href="#" name="Selected vessel (0)" wide={isOpen}>
            <ShipIcon className="w-8 min-w-8 stroke-inherit stroke-[0.75]" />
          </NavigationLink>
        </div>
      </motion.nav>
    </>
  )
}

export default LeftPanel
