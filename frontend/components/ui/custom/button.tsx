"use client"

import * as React from "react"
import Image from "next/image"
import ArrowIcon from "@/public/right-arrow.svg"

type Props = {
  title: string
  withArrowIcon?: boolean
  onClick?: () => void
}

export default function Button({ title, withArrowIcon, onClick }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex h-3/4 items-center rounded bg-color-1 pl-2 pr-4 text-xxs"
    >
      {title}

      {!!withArrowIcon && (
        <Image
          className="ml-2"
          src={ArrowIcon}
          alt="arrow icon"
          height={8}
          width={8}
        />
      )}
    </button>
  )
}
