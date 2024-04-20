import { Item } from "@/types/item"
import ListItem from "@/components/ui/list-item"

type Props = {
  title: string
  items: Item[]
  enableViewDetails?: boolean
}

export default function ListCard({ title, items, enableViewDetails }: Props) {
  return (
    <div className="min-h-50 rounded bg-color-2 pl-5 pr-10 pt-2">
      <div className="mb-3 block text-xs font-semibold uppercase text-white">
        {title}
      </div>

      {items.map((item) => (
        <ListItem
          item={item}
          key={item.id}
          enableViewDetails={enableViewDetails}
        />
      ))}
    </div>
  )
}
