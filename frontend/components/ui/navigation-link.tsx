"use client"

import Link from "next/link"

interface Props {
  children: React.ReactNode
  name: string
  wide: boolean
  href: string
  onClick?: () => void
}

const NavigationLink = ({
  children,
  name,
  href = "#",
  wide = false,
  onClick,
}: Props) => {
  return (
    <Link
      href={href}
      className="flex cursor-pointer place-items-center gap-3 p-1 text-color-panel hover:text-primary"
      onClick={onClick}
    >
      {children}
      {wide && (
        <p className="text-clip whitespace-nowrap tracking-wide text-inherit">
          {name}
        </p>
      )}
    </Link>
  )
}

export default NavigationLink
