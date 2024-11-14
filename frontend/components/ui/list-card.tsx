import { Item } from "@/types/item"
import { cn } from "@/libs/utils"
import ListItem from "@/components/ui/list-item"
import { Skeleton } from "@/components/ui/skeleton"

type Props = {
  title: string
  items: Item[]
  enableViewDetails?: boolean
  loading?: boolean
  titleClassName?: string
  skeletonCount?: number
}

export default function ListCard({
  title,
  items,
  enableViewDetails,
  loading,
  titleClassName,
  skeletonCount = 5,
}: Props) {
  const hasNoData = !!(items?.length == 0 && !loading)

  return (
    <div className="min-h-50 relative flex flex-col gap-4">
      <div
        className={cn(
          "block h-10 text-lg font-semibold uppercase text-white",
          titleClassName
        )}
      >
        {title}
      </div>
      <div className="rounded bg-color-2 p-4">
        {hasNoData && (
          <div className="text-md mb-3 block font-light text-white">
            No data found
          </div>
        )}

        {loading && (
          <>
            {[...Array(skeletonCount)].map((_, index) => (
              <Skeleton
                key={`skeleton-${index}`}
                className="mb-2 h-12 w-full opacity-10"
              />
            ))}
          </>
        )}

        {!loading &&
          items.map((item, index) => (
            <div key={item.id}>
              <ListItem item={item} enableViewDetails={enableViewDetails} />
              {index < items.length - 1 && (
                <div className="my-1 border-b border-white opacity-20" />
              )}
            </div>
          ))}
      </div>
    </div>
  )
}
