import { scanSignals, summarizeAnnotations } from '../review/scanner.js';

export function runBacktest({ days, barsByDay, strategy }) {
  return days.map((day) => {
    const bars1m = barsByDay[`${day.id}:1m`] || [];
    const bars5m = barsByDay[`${day.id}:5m`] || [];
    const annotations = scanSignals({ bars1m, bars5m, strategy });
    return { day, annotations, summary: summarizeAnnotations(annotations) };
  });
}
