import { COUNTRIES_ISO3 } from "@/constants/countries-iso3.constants"

export const getCountryNameFromIso3 = (
  countryIso3: string | null | undefined
): string => {
  if (!countryIso3) return ""
  return (
    COUNTRIES_ISO3.find((country) => country.code === countryIso3)?.name ?? ""
  )
}
