import { Button } from "@/components/ui/button"

interface FilterButtonProps {
  value: string
  label: string
  isActive: boolean
  onToggle: (value: string) => void
}

export function FilterButton({
  value,
  label,
  isActive,
  onToggle,
}: FilterButtonProps) {
  return (
    <Button
      variant="outline"
      size="sm"
      className={`h-7 w-fit justify-start font-normal hover:text-primary-foreground/90 ${
        isActive
          ? "bg-primary hover:bg-primary/90"
          : "bg-muted hover:bg-muted/50"
      }`}
      onClick={() => onToggle(value)}
    >
      {label}
    </Button>
  )
}
