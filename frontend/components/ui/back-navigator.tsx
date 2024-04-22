"use client"

import Image from "next/image"
import { useRouter } from "next/navigation"
import LeftArrowIcon from "@/public/left-arrow.svg"

export default function BackNavigator() {
  let router = useRouter()
  const onClick = () => {
    router.back()
  }

  return (
    <div className="pl-5 pt-5 hover:cursor-pointer">
      <Image
        src={LeftArrowIcon}
        alt="left arrow"
        height={30}
        width={30}
        onClick={onClick}
      />
    </div>
  )
}
