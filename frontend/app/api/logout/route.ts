import { cookies } from "next/headers"
import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const cookieStore = cookies()

  // Remove the auth cookie by setting it to expire immediately
  cookieStore.set("auth-token", "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    expires: new Date(0), // Setting to past date effectively deletes the cookie
  })

  return new NextResponse("Logged out", { status: 200 })
}
