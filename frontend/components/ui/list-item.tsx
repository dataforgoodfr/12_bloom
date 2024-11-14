"use client"

import { useRouter } from "next/navigation"
import { ChevronRight } from "lucide-react"

import { Item } from "@/types/item"
import { Button } from "@/components/ui/button"

type Props = {
  item: Item
  enableViewDetails?: boolean
}

export default function ListItem({ item, enableViewDetails }: Props) {
  const { id, title, description, value, type } = item
  const router = useRouter()
  let showViewDetailsButton = !!enableViewDetails

  const onClickViewDetails = () => {
    router.push(`/details/${type}/${id}`)
  }

  return (
    <div className="flex min-h-12 gap-8 p-0">
      <div className="w-full">
        <div className="text-md text-white">{title}</div>
        <div className="text-sm text-color-4">{description}</div>
      </div>
      <div className=" flex items-center justify-end text-sm text-white">
        {value}
      </div>
      <div className="flex items-center">
        {showViewDetailsButton && (
          <Button
            className="flex items-center gap-2 border-none text-base"
            title="View"
            onClick={onClickViewDetails}
          >
            View
            <ChevronRight className="size-4" />
          </Button>
        )}
      </div>
    </div>
  )
}
