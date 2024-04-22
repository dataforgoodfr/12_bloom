import "@/styles/globals.css"

import { Metadata } from "next"

import { siteConfig } from "@/config/site"
import { MapStoreProvider } from "@/components/providers/map-store-provider"

export const metadata: Metadata = {
  title: {
    default: "Trailwatch Map",
    template: `%s - ${siteConfig.name}`,
  },
  description: siteConfig.description,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
}

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <section className="relative flex h-screen w-full flex-row">
      <MapStoreProvider>{children}</MapStoreProvider>
    </section>
  )
}
