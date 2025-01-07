import { cn } from "@/libs/utils"
import { Button } from "@/components/ui/button"

interface FilterButtonProps {
  children: React.ReactNode
  isActive: boolean
  onClick: () => void
  className?: string
}

export function FilterButton({
  children,
  isActive,
  onClick,
  className,
}: FilterButtonProps) {
  return (
    <Button
      variant="outline"
      className={cn(
        "h-8",
        isActive
          ? "bg-primary text-black hover:bg-primary/90"
          : "bg-gray-100 text-black hover:bg-gray-200 hover:text-black",
        className
      )}
      onClick={onClick}
    >
      {children}
    </Button>
  )
}
