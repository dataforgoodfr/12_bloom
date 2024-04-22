import DashboardHeader from "@/components/dashboard/dashboard-header"
import DashboardOverview from "@/components/dashboard/dashboard-overview"

export default function DashboardPage() {
  return (
    <section className="h-svh bg-color-3 px-6">
      <div className="block h-1/6 w-full">
        <DashboardHeader />
      </div>

      <div className="h-5/6 w-full">
        <DashboardOverview />
      </div>
    </section>
  )
}
