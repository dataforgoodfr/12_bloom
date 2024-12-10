import { cn } from "@/libs/utils"
import * as React from "react"

type Props = {
  description: string
  onClick?: () => void
  children: React.ReactNode
  disabled?: boolean
  className?: string
}

export default function IconButton({
  onClick,
  children,
  description,
  disabled,
  className,
}: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "me-2 inline-flex size-10 items-center justify-center rounded-full bg-white text-center text-sm font-medium text-black shadow-md hover:bg-slate-200 focus:outline-none focus:ring-4 focus:ring-slate-300 dark:bg-slate-600 dark:hover:bg-slate-700 dark:focus:ring-slate-800",
        className
      )}
    >
      {children}
      <span className="sr-only">{description}</span>
    </button>
  )
}
