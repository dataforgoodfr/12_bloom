import { useMemo } from "react"
import PortIcon from "@/public/icons/port.svg"
import { IconLayer } from "deck.gl"
import { useShallow } from "zustand/react/shallow"

import { Port } from "@/types/port"
import { useLoaderStore, usePortsStore } from "@/libs/stores"

export const usePortsLayers = () => {
  const { portsLoading } = useLoaderStore(
    useShallow((state) => ({
      portsLoading: state.portsLoading,
    }))
  )

  const { ports } = usePortsStore(
    useShallow((state) => ({
      ports: state.ports,
    }))
  )

  const portsLayer = useMemo(() => {
    return new IconLayer<Port>({
      id: `ports`,
      data: ports,
      getPosition: (port: Port) => [port.longitude, port.latitude],
      getIcon: (d: Port) => ({
        url: "/icons/port.svg",
        width: 34,
        height: 34,
      }),
      onClick: (info) => {
        window.open(info.object.url, "_blank")
      },
      pickable: true,
      sizeScale: 5000,
      sizeUnits: "meters",
      sizeMinPixels: 2,
      sizeMaxPixels: 34,
    })
  }, [ports])

  if (portsLoading) return []

  return [portsLayer]
}
