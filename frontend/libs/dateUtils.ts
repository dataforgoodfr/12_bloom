export function convertDurationInSeconds(durationPattern?: string): number {
  if (!durationPattern) return 0

  const matches = durationPattern.match(
    /P(?:(\d+)Y)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?/
  )

  if (!matches) {
    throw new Error("Invalid duration pattern")
  }

  const [
    _,
    years = "0",
    days = "0",
    hours = "0",
    minutes = "0",
    seconds = "0",
  ] = matches

  const totalSeconds =
    parseInt(years) * 365 * 24 * 60 * 60 + // converting years to hours (approximate)
    parseInt(days) * 24 * 60 * 60 +
    parseInt(hours) * 60 * 60 +
    parseInt(minutes) * 60 +
    parseFloat(seconds)

  return Math.floor(totalSeconds)
}

export function convertDurationToString(durationPattern: string): string {
  const totalSeconds = convertDurationInSeconds(durationPattern)
  const totalHours = totalSeconds / 3600

  const years = Math.floor(totalHours / (24 * 365))
  const remainingHoursAfterYears = totalHours % (24 * 365)
  const days = Math.floor(remainingHoursAfterYears / 24)
  const hours = Math.floor(remainingHoursAfterYears % 24)
  const minutes = Math.floor((totalSeconds % 3600) / 60)

  const parts = []
  if (years > 0) parts.push(`${years}y`)
  if (days > 0) parts.push(`${days}d`)
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)

  return parts.length > 0 ? parts.join(" ") : "0h"
}

export function getDateRange(days: number) {
  const today = new Date()
  const start = new Date(today)
  start.setDate(today.getDate() - days)
  start.setHours(0, 0, 0, 0)

  today.setHours(23, 59, 59, 999)

  return {
    startAt: start.toISOString(),
    endAt: today.toISOString(),
  }
}

export function formatDuration(tsInSeconds: number): string {
  const hours = Math.floor(tsInSeconds / 3600)
  const minutes = Math.floor((tsInSeconds - hours * 3600) / 60)
  const seconds = tsInSeconds - hours * 3600 - minutes * 60
  return `${hours}h ${minutes}m ${seconds}s`
}
