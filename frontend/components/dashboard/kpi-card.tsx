import { Loader2 } from "lucide-react"

import Spinner from "../ui/custom/spinner"
import { Skeleton } from "../ui/skeleton"

type Props = {
  title: string
  kpiValue: number
  kpiUnit?: string
  totalValue: number
  totalUnit?: string
  loading?: boolean
}

export default function KPICard({
  title,
  kpiValue,
  kpiUnit,
  totalUnit,
  totalValue,
  loading,
}: Props) {
  return (
    <div className="flex w-full flex-col gap-y-2 rounded bg-primary p-4">
      <div className="block text-lg font-bold uppercase">{title}</div>
      <div className="flex flex-row items-end justify-end">
        <div className="h-[40px] min-w-[50px] text-4xl font-bold uppercase">
          {loading ? (
            <div className="flex flex-row items-center justify-center">
              <Spinner />
            </div>
          ) : (
            `${kpiValue}`
          )}
        </div>
        <div className="ml-2 inline text-base font-bold uppercase">
          {`${kpiUnit || ""} / ${totalValue} ${totalUnit || ""}`}
        </div>
      </div>
    </div>
  )
}
