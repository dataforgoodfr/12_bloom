export function convertDurationInHours(durationPattern: string): number {
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

  return Math.floor(totalHours)
}

// format date like: 2023-07-15T17:16:27
export function format(date: Date) {
  return (
    [
      date.getFullYear(),
      padTwoDigits(date.getMonth() + 1),
      padTwoDigits(date.getDate()),
    ].join("-") +
    "T" +
    [
      padTwoDigits(date.getHours()),
      padTwoDigits(date.getMinutes()),
      padTwoDigits(date.getSeconds()),
    ].join(":")
  )
}

function padTwoDigits(num: number) {
  return num.toString().padStart(2, "0")
}
