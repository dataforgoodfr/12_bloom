import LeftPanel from "@/components/core/left-panel"
import MapControls from "@/components/core/map-controls"
import DemoMap from "@/components/core/map/main-map"

export default function MapPage() {
  return (
    <>
      <LeftPanel />
      <DemoMap />
      <MapControls />
    </>
  )
}
