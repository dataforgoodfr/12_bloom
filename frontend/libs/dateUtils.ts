export function convertDurationInHours(durationPattern: string): string {
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

  const totalHours =
    parseInt(years) * 365 * 24 + // converting years to hours (approximate)
    parseInt(days) * 24 +
    parseInt(hours) +
    parseInt(minutes) / 60 +
    parseFloat(seconds) / 3600

  return Math.round(totalHours).toLocaleString("fr-FR")
}

function padTwoDigits(num: number) {
  return num.toString().padStart(2, "0")
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
