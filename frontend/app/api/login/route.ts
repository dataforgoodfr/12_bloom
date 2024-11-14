import { cookies } from "next/headers"
import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const { password } = await request.json()

  if (password === process.env.APP_PASSWORD) {
    const cookieStore = cookies()

    cookieStore.set("auth-token", "authenticated", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      expires: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    })

    return new NextResponse("Logged in", { status: 200 })
  }

  return new NextResponse("Invalid password", { status: 401 })
}
