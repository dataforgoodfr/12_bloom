"use client"

import Link from "next/link"

interface Props {
  children: React.ReactNode
  name: string
  wide: boolean
  href: string
}

const NavigationLink = ({
  children,
  name,
  href = "#",
  wide = false,
}: Props) => {
  return (
    <Link
      href={href}
      className="group flex cursor-pointer place-items-center gap-3 rounded stroke-neutral-200 p-1 text-neutral-200 transition-colors duration-100 hover:stroke-foreground hover:font-semibold hover:text-card"
    >
      {children}
      {wide && (
        <p className="text-clip whitespace-nowrap font-unito tracking-wide text-inherit">
          {name}
        </p>
      )}
    </Link>
  )
}

export default NavigationLink
