import BackNavigator from "@/components/ui/back-navigator"

interface RootLayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: RootLayoutProps) {
  return (
    <div className="h-full">
      <BackNavigator />
      <div className="pl-20 pr-2 pt-24">{children}</div>
    </div>
  )
}
