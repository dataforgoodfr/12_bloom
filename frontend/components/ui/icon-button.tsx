import * as React from "react"

type Props = {
  description: string
  onClick?: () => void
  children: React.ReactNode
  disabled?: boolean
}

const IconButton: React.FC<Props> = ({
  onClick,
  children,
  description,
  disabled,
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="me-2 inline-flex size-10 items-center justify-center rounded-full bg-white text-center text-sm font-medium text-black shadow-md hover:bg-slate-200 focus:outline-none focus:ring-4 focus:ring-slate-300 dark:bg-slate-600 dark:hover:bg-slate-700 dark:focus:ring-slate-800"
    >
      {children}
      <span className="sr-only">{description}</span>
    </button>
  )
}

export default IconButton
