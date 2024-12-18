import vesselAtlas from "@/public/img/vessel_atlas.json"
import type { PickingInfo } from "@deck.gl/core"
import { IconMapping } from "@deck.gl/layers/src/icon-layer/icon-manager"

export const getPickObjectType = (
  info: PickingInfo
): "vessel" | "excursion" | "zone" | "segmentPosition" | "port" | null => {
  const { object } = info

  if (!object) return null

  // @ts-ignore
  if (object?.properties?.excursion_id) {
    return "excursion"
  }

  if (object?.type === "segmentPosition") {
    return "segmentPosition"
  }

  if ("vessel" in object) {
    return "vessel"
  }

  if ("locode" in object && "url" in object) {
    return "port"
  }

  if ("geometry" in object) {
    return "zone"
  }

  return null
}

export type VesselIconName =
  | "noHeading"
  | "noHeadingOutline"
  | "withHeading"
  | "withHeadingOutline"
  | "selectionHalo"

export const getDeckGLIconMapping = (): IconMapping => {
  const filenameIconMapping: { [key: string]: VesselIconName } = {
    "vessel-no-heading.png": "noHeading",
    "vessel-no-heading-outline.png": "noHeadingOutline",
    "vessel.png": "withHeading",
    "vessel-outline.png": "withHeadingOutline",
    "selection-halo.png": "selectionHalo",
  }
  const iconMapping: IconMapping = {}
  vesselAtlas.frames.forEach((frame) => {
    iconMapping[filenameIconMapping[frame.filename]] = {
      x: frame.frame.x,
      y: frame.frame.y,
      width: frame.frame.w,
      height: frame.frame.h,
      anchorX: frame.frame.w / 2,
      anchorY: frame.frame.h / 2,
      mask: true,
    }
  })
  return iconMapping
}
