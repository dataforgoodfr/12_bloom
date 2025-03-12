"use client"

import { AnimatePresence, motion } from "motion/react"

import { useMapStore } from "@/libs/stores/map-store"
import PreviewCard from "@/components/core/map/preview-card"

export interface PositionPreviewTypes {}

const PositionPreview: React.FC<PositionPreviewTypes> = () => {
  const activePosition = useMapStore((state) => state.activePosition)

  return (
    <AnimatePresence>
      {activePosition && (
        <motion.div
          id="preview-card-wrapper"
          initial={{ y: 300, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 300, opacity: 0 }}
          transition={{ type: "spring", stiffness: 66 }}
          className="fixed bottom-0 right-0 mb-2 mr-10 w-auto -translate-x-1/2"
        >
          <PreviewCard vesselInfo={activePosition} />
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default PositionPreview
