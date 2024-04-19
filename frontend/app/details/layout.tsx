import BackNavigator from "@/components/ui/back-navigator"

interface RootLayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: RootLayoutProps) {
  return (
    <div className="h-svh bg-color-2">
      <BackNavigator />
      <div className="pl-20 pr-2 pt-24">{children}</div>
    </div>
  )
}
