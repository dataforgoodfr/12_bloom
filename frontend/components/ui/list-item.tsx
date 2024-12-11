"use client"

import { useRouter } from "next/navigation"
import { COUNTRIES_ISO3 } from "@/constants/countries-iso3.constants"
import { getCountryNameFromIso3 } from "@/utils/vessel.utils"
import { ChevronRight } from "lucide-react"

import { Item } from "@/types/item"
import { Button } from "@/components/ui/button"

type Props = {
  item: Item
  enableViewDetails?: boolean
}

export default function ListItem({ item, enableViewDetails }: Props) {
  const { id, title, description, value, type, countryIso3 } = item
  const router = useRouter()
  let showViewDetailsButton = !!enableViewDetails

  const onClickViewDetails = () => {
    router.push(`/details/${type}/${id}`)
  }

  const countryLabel = getCountryNameFromIso3(countryIso3)

  return (
    <div
      className={`flex min-h-12 gap-4 ${showViewDetailsButton ? "p-0" : "p-2"}`}
    >
      <div className="flex-1">
        <div className="text-md text-white">{title}</div>
        <div className="text-sm text-color-4">{description}</div>
      </div>
      {type === "vessel" && (
        <div className="flex w-24 items-center text-sm text-white">
          {countryLabel}
        </div>
      )}
      <div className="flex w-32 items-center justify-end text-sm text-white">
        {value}
      </div>
      {showViewDetailsButton && (
        <div className="flex w-24 items-center">
          <Button
            className="flex items-center gap-2 border-none text-base"
            title="View"
            onClick={onClickViewDetails}
          >
            View
            <ChevronRight className="size-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
