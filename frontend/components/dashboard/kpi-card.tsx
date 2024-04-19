type Props = {
  title: string
  kpiValue: number
  kpiUnit?: string
  totalValue: number
  totalUnit?: string
}

export default function KPICard(props: Props) {
  let { title, kpiValue, kpiUnit, totalUnit, totalValue } = props
  kpiUnit = kpiUnit ?? ""
  totalUnit = totalUnit ?? ""

  return (
    <div className="container h-24 w-full rounded bg-color-1 pl-3 pt-3">
      <div className="mb-4 block text-xxs font-bold uppercase">{title}</div>
      <div className="inline text-4xl font-bold uppercase">{`${kpiValue}`}</div>
      <div className="ml-2 inline text-base font-bold uppercase">
        {`${kpiUnit}`} / {`${totalValue} ${totalUnit}`}
      </div>
    </div>
  )
}
