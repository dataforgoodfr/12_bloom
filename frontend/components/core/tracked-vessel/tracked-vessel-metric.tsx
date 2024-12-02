import { Progress } from "@/components/ui/progress"
import { cn } from "@/libs/utils"
import Toggle from "@/components/ui/custom/toggle"

export interface TrackedVesselMetricProps {
  title: string
  value: number
  unit?: 'time'
  baseValue?: number
  children?: React.ReactNode
}

export default function TrackedVesselMetric({ title, value, baseValue, children, unit }: TrackedVesselMetricProps) {
  return children ? (
    <Toggle.Root className="w-full justify-between">
      <Toggle.Header>
        <TrackedVesselMetricHeader title={title} value={value} baseValue={baseValue} unit={unit} />
      </Toggle.Header>
      <Toggle.Content>
        {children}
      </Toggle.Content>
    </Toggle.Root>
  ) : (
    <TrackedVesselMetricHeader title={title} value={value} baseValue={baseValue} unit={unit} />
  )
}


function TrackedVesselMetricHeader({ title, value, baseValue, children, unit }: TrackedVesselMetricProps) {
  const prettifyTime = (timeInSeconds: number) => {
    const days = Math.floor(timeInSeconds / 86400)
    const hours = Math.floor((timeInSeconds % 86400) / 3600)
    const minutes = Math.floor((timeInSeconds % 3600) / 60)

    let prettifiedTime = ""
    if (days > 0) prettifiedTime += `${days}d `
    if (hours > 0) prettifiedTime += `${hours}h `
    if (minutes > 0) prettifiedTime += `${minutes}mn`

    return prettifiedTime
  }

  const showProgress = baseValue !== undefined
  const progressValue = showProgress ? Number(((Number(value) / Number(baseValue)) * 100).toFixed(1)) : 0

  const prettyValue = unit === 'time' ? prettifyTime(Number(value)) : value
  const valueFontSize = showProgress ? 'text-xs' : 'text-sm'

  return (
    <div className="flex flex-col">
      <div className="flex justify-between items-center">
        <h6 className="text-sm font-semibold">{title}</h6>
        <span className={cn("text-sm text-color-4", valueFontSize)}>{prettyValue}</span>
      </div>
      {showProgress && (
        <div className="w-full flex flex-col">
          <p className="text-xs text-progress-color-1">{progressValue}%</p>
          <Progress value={progressValue} className="w-full rounded-full h-1 bg-color-3" indicatorColor="bg-progress-color-1"/>
        </div>
      )}
      {children}
    </div>
  )
}
