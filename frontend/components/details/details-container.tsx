import { ItemDetails } from "@/types/item"
import ListCard from "@/components/ui/list-card"

type Props = {
  details: ItemDetails
}

export default function DetailsContainer({ details }: Props) {
  const { label, description, relatedItemsType, relatedItems } = details

  return (
    <div className="grid grid-cols-5 gap-x-32">
      <div className="col-span-2">
        <div className="mb-5 text-3xl font-semibold text-white">{label}</div>
        <div className="block text-justify text-xs font-light leading-relaxed text-white">
          {description}
        </div>
      </div>
      <div className="col-span-3">
        <ListCard title={relatedItemsType} items={relatedItems} />
      </div>
    </div>
  )
}
