export function convertDurationInSeconds(durationPattern: string): number {
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

export function convertDurationInHours(durationPattern: string): number {
  return convertDurationInSeconds(durationPattern) / 3600
}

export function getDateRange(days: number) {
  const today = new Date()
  const start = new Date(today)
  start.setDate(today.getDate() - days)
  start.setHours(0, 0, 0, 0)

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
