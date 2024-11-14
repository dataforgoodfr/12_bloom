import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select"

type DateRangeSelectorProps = {
  onValueChange: (value: string) => void
  disabled?: boolean
  defaultValue?: string
  className?: string
}

const DATE_RANGE_OPTIONS = [
  { label: "Last 7 days", value: "7" },
  { label: "Last 15 days", value: "15" },
  { label: "Last month", value: "30" },
  { label: "Last year", value: "365" },
]

export function DateRangeSelector({
  onValueChange,
  disabled = false,
  defaultValue,
  className = "float-right w-40",
}: DateRangeSelectorProps) {
  return (
    <Select
      onValueChange={onValueChange}
      defaultValue={defaultValue || DATE_RANGE_OPTIONS[0].value}
    >
      <SelectTrigger
        className={`${className} border border-input bg-background text-white hover:bg-accent hover:text-white`}
        disabled={disabled}
      >
        <SelectValue placeholder="Date range" />
      </SelectTrigger>
      <SelectContent className="bg-background text-white">
        {DATE_RANGE_OPTIONS.map((option) => (
          <SelectItem
            key={option.value}
            value={option.value}
            className="text-white data-[highlighted]:bg-accent data-[highlighted]:text-white"
          >
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
