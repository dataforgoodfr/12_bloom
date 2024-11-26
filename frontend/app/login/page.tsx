"use client"

import { useState } from "react"
import Image from "next/image"
import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function Login() {
  const router = useRouter()
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      })

      if (response.ok) {
        router.push("/dashboard") // or wherever you want to redirect after login
      } else {
        setError("Invalid password")
      }
    } catch (err) {
      setError("An error occurred. Please try again.")
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="grid h-[400px] w-full max-w-3xl overflow-hidden rounded-lg bg-card md:grid-cols-2">
        <div className="relative h-full">
          <Image
            src="/img/login-cover.jpg"
            alt="Login waves visual"
            fill
            className="object-cover"
            priority
            quality={85}
            sizes="(max-width: 768px) 100vw, 50vw"
          />
        </div>
        <form
          onSubmit={handleSubmit}
          className="flex size-full  flex-col items-center justify-between space-y-4 p-8"
        >
          <div className="mb-6 space-y-2 text-center">
            <h1 className="text-2xl font-bold">Welcome to TrawlWatch</h1>
          </div>
          <div className="space-y-2">
            <p>Enter your password to access your account</p>

            <Input
              id="password"
              type="password"
              className="w-full bg-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className=" text-sm text-red-500">{error}</p>}
          </div>
          <Button type="submit" className="w-full">
            Log in
          </Button>
        </form>
      </div>
    </div>
  )
}
