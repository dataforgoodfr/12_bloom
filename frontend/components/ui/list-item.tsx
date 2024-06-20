"use client"

import { useRouter } from "next/navigation"

import { Item } from "@/types/item"
import Button from "@/components/ui/custom/button"

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
    <div className="my-1.5 flex">
      <div className="flex w-full border-b-1 border-color-5">
        <div className="w-full pb-1">
          <div className="text-xxs text-white">{title}</div>
          <div className="text-xxxs text-color-4">{description}</div>
        </div>
        <div className="block text-sm text-white">{value}</div>
      </div>
      <div className="ml-6 flex">
        {showViewDetailsButton && (
          <Button title="View" withArrowIcon onClick={onClickViewDetails} />
        )}
      </div>
    </div>
  )
}
