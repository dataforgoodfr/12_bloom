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
      className="flex cursor-pointer place-items-center gap-3 rounded stroke-neutral-400 stroke-[0.75] p-1 text-neutral-400 transition-colors duration-100 hover:bg-neutral-700/30 hover:stroke-neutral-100 hover:text-neutral-100"
    >
      {children}
      {wide && (
        <p className="font-unito text-clip whitespace-nowrap tracking-wide text-inherit">
          {name}
        </p>
      )}
    </Link>
  )
}

export default NavigationLink
