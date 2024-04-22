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
        className="p-1 w-full text-white bg-color-3 text-xxs"
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
