import Image from "next/image"

export default function PartnerCredits() {
  return (
    <div className="fixed bottom-2 left-2 z-50 flex justify-around gap-4 rounded-full bg-color-2/30 p-5 hover:bg-color-2/50">
      <Image src="/img/bloom-logo.png" alt="Logo" width={50} height={50} />
      <Image
        src="/img/data-for-good-logo.png"
        alt="Logo"
        width={50}
        height={50}
      />
    </div>
  )
}
