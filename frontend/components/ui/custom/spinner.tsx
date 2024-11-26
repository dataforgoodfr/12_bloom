import { Loader2 } from "lucide-react"

import { cn } from "@/libs/utils"

export default function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn("size-8 animate-spin", className)} />
}
