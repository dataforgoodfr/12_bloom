import Image from "next/image";

<<<<<<< HEAD




=======
>>>>>>> 36eda0428e6a54e241428b7e572bf4897663d922
interface Props {
  wide: boolean
}

<<<<<<< HEAD
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
=======
export default function PartnerCredits({ wide = false }: Props) {
  return (
    <div
      className={`z-50 flex items-center justify-around gap-2 text-xs font-bold ${wide ? "block" : "hidden"}`}
    >
      <p>by</p>
      <a
        href="https://bloomassociation.org"
        target="_blank"
        rel="noopener noreferrer"
      >
        <Image src="/img/bloom-logo.png" alt="Logo" width={60} height={50} />
      </a>
      <p className="text-base">&</p>
      <a
        href="https://dataforgood.fr/"
        target="_blank"
        rel="noopener noreferrer"
      >
>>>>>>> 36eda0428e6a54e241428b7e572bf4897663d922
        <Image
          src="/img/data-for-good-logo.png"
          alt="Logo"
          width={90}
          height={50}
<<<<<<< HEAD
          />
=======
        />
>>>>>>> 36eda0428e6a54e241428b7e572bf4897663d922
      </a>
    </div>
  )
}