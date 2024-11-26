import BackNavigator from "@/components/ui/back-navigator"

interface RootLayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: RootLayoutProps) {
  return (
    <div className="relative h-full">
      <BackNavigator />
      <div className="mx-auto flex max-w-[90%] flex-col justify-center">
        {children}
      </div>
    </div>
  )
}
