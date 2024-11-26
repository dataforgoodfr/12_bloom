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
    <div className="flex h-full justify-center">
      <div className="flex h-screen max-h-[850px] w-full max-w-screen-xl flex-col items-start gap-8 overflow-hidden py-8 xl:gap-16">
        <div className="flex shrink-0 flex-col gap-0">
          <div className="text-3xl font-bold text-white">{label}</div>
          <div className="block text-justify text-xl font-light leading-relaxed text-white">
            {description}
          </div>
        </div>
        <div className="grid min-h-0 w-full flex-1 grid-cols-2 gap-8 xl:gap-16">
          <Card className="relative h-full overflow-hidden">
            <Image
              src={"/img/placeholder-zone.png"}
              alt={"Zone map image"}
              className="object-cover"
              fill
            />
          </Card>
          <div className="relative flex h-full min-h-0 flex-1 flex-col">
            <div className="absolute right-0 top-0 z-10">
              <DateRangeSelector
                onValueChange={onDateRangeChange}
                defaultValue={defaultDateRange || "7"}
                disabled={isLoading}
              />
            </div>
            <div className="h-full min-h-0 flex-1">
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
    </div>
  )
}
