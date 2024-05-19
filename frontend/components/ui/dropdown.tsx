"use client"

import { FormEvent } from "react"

type Props = {
  options: string[]
  className?: string
  onSelect: (value: string) => void
}

export default function Dropdown({ className, options, onSelect }: Props) {
  return (
    <form
      className={className}
      onChange={(event: FormEvent<HTMLFormElement>) =>
        onSelect((event.target as HTMLSelectElement).value)
      }
    >
      <select
        id="countries"
        className="w-full bg-color-3 p-1 text-xxs text-white"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </form>
  )
}
