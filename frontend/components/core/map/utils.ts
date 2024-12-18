import type { PickingInfo } from "@deck.gl/core"

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
