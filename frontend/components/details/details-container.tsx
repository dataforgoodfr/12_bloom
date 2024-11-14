import Image from "next/image"

import { ItemDetails } from "@/types/item"
import ListCard from "@/components/ui/list-card"

import { Card } from "../ui/card"
import { DateRangeSelector } from "../ui/date-range-selector"

type Props = {
  details: ItemDetails | null
  onDateRangeChange: (value: string) => void
  defaultDateRange: string
  isLoading: boolean
}

export default function DetailsContainer({
  details,
  onDateRangeChange,
  defaultDateRange,
  isLoading,
}: Props) {
  if (!details) {
    return null
  }

  const { label, description, relatedItemsType, relatedItems } = details

  return (
    <div className="flex justify-center">
      <div className="grid max-w-screen-xl grid-cols-2 items-start justify-start gap-16">
        <div className="flex flex-col items-start gap-8">
          <div className="flex flex-col gap-0">
            <div className="text-3xl font-bold text-white">{label}</div>
            <div className="block text-justify text-xl font-light leading-relaxed text-white">
              {description}
            </div>
          </div>
          <Card className="relative h-[500px] w-full overflow-hidden">
            <Image
              src={"/img/placeholder-zone.png"}
              alt={"Zone map image"}
              className="object-cover"
              fill
            />
          </Card>
        </div>
        <div className="relative flex flex-col">
          <div className="absolute right-0 top-0 z-10">
            <DateRangeSelector
              onValueChange={onDateRangeChange}
              defaultValue={defaultDateRange || "7"}
              disabled={isLoading}
            />
          </div>
          <div className="col-span-3">
            <ListCard
              title={relatedItemsType}
              items={relatedItems}
              loading={isLoading}
              skeletonCount={10}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
