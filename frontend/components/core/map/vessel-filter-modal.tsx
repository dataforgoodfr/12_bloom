"use client"

import { useEffect, useMemo, useState } from "react"
import { COUNTRIES_ISO3 } from "@/constants/countries-iso3.constants"
import {
  getCountries,
  getVesselClasses,
  getVesselTypes,
} from "@/services/backend-rest-client"
import { SlidersHorizontal } from "lucide-react"
import { useShallow } from "zustand/react/shallow"

import { useVesselsStore } from "@/libs/stores/vessels-store"
import { MultiSelect } from "@/components/ui/custom/multiselect"

import { MapFilterModal } from "./map-filter-modal"

interface VesselFilterModalProps {
  isLoading: boolean
}

export default function VesselFilterModal({
  isLoading,
}: VesselFilterModalProps) {
  const [vesselClasses, setVesselClasses] = useState<string[]>([])
  const [vesselTypes, setVesselTypes] = useState<string[]>([])
  const [countries, setCountries] = useState<string[]>([])
  const [isFiltersLoading, setIsFiltersLoading] = useState(true)

  useEffect(() => {
    const fetchFilters = async () => {
      const [classes, types, countries] = await Promise.all([
        getVesselClasses().then((res) => res.data),
        getVesselTypes().then((res) => res.data),
        getCountries().then((res) => res.data),
      ])
      setVesselClasses(classes)
      setVesselTypes(types)
      setCountries(countries)
      setIsFiltersLoading(false)
    }

    fetchFilters()
  }, [])

  const {
    typeFilter,
    classFilter,
    countryFilter,
    setTypeFilter,
    setClassFilter,
    setCountryFilter,
  } = useVesselsStore(
    useShallow((state) => ({
      typeFilter: state.typeFilter,
      classFilter: state.classFilter,
      countryFilter: state.countryFilter,
      setTypeFilter: state.setTypeFilter,
      setClassFilter: state.setClassFilter,
      setCountryFilter: state.setCountryFilter,
    }))
  )

  const classesOptions = useMemo(() => {
    return vesselClasses
      .map((c) => ({ value: c, label: c }))
      .sort((a, b) => {
        if (a.label === "> 80 m") return 1
        return a.label.localeCompare(b.label)
      })
  }, [vesselClasses])

  const typesOptions = useMemo(() => {
    return vesselTypes
      .map((t) => ({ value: t, label: t }))
      .sort((a, b) => a.label.localeCompare(b.label))
  }, [vesselTypes])

  const countriesOptions = useMemo(() => {
    return countries
      .map((c) => ({
        value: c,
        label: COUNTRIES_ISO3.find((cc) => cc.code === c)?.name || c,
      }))
      .sort((a, b) => a.label.localeCompare(b.label))
  }, [countries])

  return (
    <MapFilterModal
      icon={SlidersHorizontal}
      title="Filters"
      description="Configure vessel display filters"
      loading={isLoading || isFiltersLoading}
      disabled={isLoading || isFiltersLoading}
      filterCount={
        typeFilter.length + classFilter.length + countryFilter.length
      }
    >
      <div className="container mx-auto p-4">
        <div className="flex flex-col gap-4">
          <MultiSelect
            title="Class"
            placeholder="Select classes"
            variant="secondary"
            options={classesOptions}
            defaultValue={classFilter}
            onValueChange={setClassFilter}
          />
          <MultiSelect
            title="Type"
            placeholder="Select types"
            variant="secondary"
            options={typesOptions}
            defaultValue={typeFilter}
            onValueChange={setTypeFilter}
          />
          <MultiSelect
            title="Country"
            placeholder="Select countries"
            variant="secondary"
            options={countriesOptions}
            defaultValue={countryFilter}
            onValueChange={setCountryFilter}
          />
        </div>
      </div>
    </MapFilterModal>
  )
}
