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
    <div className="relative flex h-full min-h-52 flex-1 flex-col gap-4">
      <div
        className={cn(
          "block h-10 text-lg font-semibold uppercase text-white",
          titleClassName
        )}
      >
        {title}
      </div>
      <div className="h-full flex-1 overflow-y-scroll rounded bg-color-2 px-2 py-1 xl:p-4">
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
                className="mb-1 h-12 w-full opacity-10 xl:mb-2 xl:h-12"
              />
            ))}
          </>
        )}

        {!loading &&
          items.map((item, index) => (
            <div key={item.id}>
              <ListItem item={item} enableViewDetails={enableViewDetails} />
              {index < items.length - 1 && (
                <div className="my-0.5 border-b border-white opacity-20" />
              )}
            </div>
          ))}
      </div>
    </div>
  )
}
