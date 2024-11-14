import Image from "next/image"

export default function Loading() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background">
      <Image
        src="/icons/boat-animated.svg"
        alt="Loading animation"
        width={100}
        height={100}
        priority
      />
    </div>
  )
}
