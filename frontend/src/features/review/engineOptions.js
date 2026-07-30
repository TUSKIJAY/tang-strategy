export const DAILY_REVIEW_ENGINE_OPTIONS = {
  maSet: ['m5', 'm10', 'm20', 'm30', 'm50', 'm60', 'm120', 'm200', 'vw'],
  allowVerticalDrag: false,
  storageNamespace: 'kline.dailyReview',
  showClippedMAIndicators: true,
};

// Review and Static Review first paint every available bar of the displayed
// day/session instead of the engine's default width-based tail window. Other
// DAILY_REVIEW_ENGINE_OPTIONS consumers (e.g. the trader point editor) keep
// the default tail-window first paint.
export const REVIEW_STATIC_ENGINE_OPTIONS = {
  ...DAILY_REVIEW_ENGINE_OPTIONS,
  initialViewport: 'full',
};
