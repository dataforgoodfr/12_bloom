
import { Temporal } from '@js-temporal/polyfill';

export function convertDurationInHours(durationPattern: string): number {
  const duration = Temporal.Duration.from(durationPattern);
  const durationHours = duration.total({ relativeTo: Temporal.Now.plainDateISO(), unit: "hours"})
  return ~~durationHours; // round without decimals
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
  );
}

function padTwoDigits(num: number) {
  return num.toString().padStart(2, "0");
}
