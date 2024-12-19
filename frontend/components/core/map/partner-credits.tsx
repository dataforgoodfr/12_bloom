import Image from "next/image";





interface Props {
  wide: boolean
}

export default function PartnerCredits({
  wide = false,
}: Props) {
  return (
    <div className={`text-xs font-bold z-50 flex justify-around items-center gap-2 ${wide ? "block" : "hidden"}`}>
      <p>by</p>
      <a href="https://bloomassociation.org" target="_blank">
        <Image src="/img/bloom-logo.png" alt="Logo" width={60} height={50} />
      </a>
      <p className="text-base">&</p>
      <a href="https://dataforgood.fr/" target="_blank">
        <Image
          src="/img/data-for-good-logo.png"
          alt="Logo"
          width={90}
          height={50}
          />
      </a>
    </div>
  )
}