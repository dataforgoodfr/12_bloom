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
      className="primary flex items-center rounded pl-2 pr-4"
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
