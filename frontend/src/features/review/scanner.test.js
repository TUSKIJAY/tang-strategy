import assert from 'node:assert/strict';
import test from 'node:test';

import { scanSignals } from './scanner.js';

function timeAt(offset) {
  const total = 9 * 60 + 30 + offset;
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
}

function sessionBars({ setupOffset, breakoutOffset = null, length = 390, gapOffset = null }) {
  return Array.from({ length }, (_, offset) => offset)
    .filter((offset) => offset !== gapOffset)
    .map((offset) => {
      const setup = offset === setupOffset;
      const breakout = offset === breakoutOffset;
      return {
        t: timeAt(offset),
        O: setup ? 9 : 10,
        H: breakout ? 11.5 : 10,
        L: 8,
        C: breakout ? 11 : (setup ? 9.5 : 9),
        m10: 9,
      };
    });
}

const bars5m = [{ t: '09:30', m10: 2, m50: 1 }];
const strategy = {
  signals: [{ id: 'call', direction: 'CALL', conditions: { candle_color: 'green' } }],
  entry_activation: {
    enabled: true,
    max_wait_bars: 8,
    confirm_price: 'close',
    require_same_direction_bar: false,
    require_ma10_slope_still_aligned: false,
  },
};

function outcomes(bars1m) {
  return scanSignals({ bars1m, bars5m, strategy });
}

test('a proven session finalizes a last-bar setup as session-end 0/8 expiry', () => {
  const annotations = outcomes(sessionBars({ setupOffset: 389 }));
  const expired = annotations.find((item) => item.type === 'expired');
  assert.equal(expired?._expiry_kind, 'session_end');
  assert.equal(expired?._activation_observed_bars, 0);
  assert.equal(expired?._activation_window_bars, 8);
  assert.equal(expired?._setup_time, '15:59');
  assert.equal(expired?._expire_time, '15:59');
});

test('session-end expiry counts valid processed probes instead of array distance', () => {
  const annotations = outcomes(sessionBars({ setupOffset: 386 }));
  const expired = annotations.find((item) => item.type === 'expired');
  assert.equal(expired?._expiry_kind, 'session_end');
  assert.equal(expired?._activation_observed_bars, 3);
  assert.equal(expired?._expire_time, '15:59');
});

test('ordinary timeout remains an 8/8 activation-window expiry', () => {
  const annotations = outcomes(sessionBars({ setupOffset: 1 }));
  const expired = annotations.find((item) => item.type === 'expired');
  assert.equal(expired?._expiry_kind, 'activation_window');
  assert.equal(expired?._activation_observed_bars, 8);
  assert.equal(expired?._setup_time, '09:31');
});

test('activation before session end is preserved', () => {
  const annotations = outcomes(sessionBars({ setupOffset: 388, breakoutOffset: 389 }));
  const activated = annotations.find((item) => item.type === 'signal');
  assert.equal(activated?._activation_time, '15:59');
  assert.equal(activated?._activation_observed_bars, 1);
  assert.equal(annotations.some((item) => item.type === 'expired'), false);
});

test('partial intraday input remains pending', () => {
  const annotations = outcomes(sessionBars({ setupOffset: 388, length: 389 }));
  assert.equal(annotations.some((item) => item.type === 'setup'), true);
  assert.equal(annotations.some((item) => item.type === 'expired'), false);
});

test('a gapped input remains pending even when its final timestamp is 15:59', () => {
  const annotations = outcomes(sessionBars({ setupOffset: 389, gapOffset: 120 }));
  assert.equal(annotations.some((item) => item.type === 'setup'), true);
  assert.equal(annotations.some((item) => item.type === 'expired'), false);
});
