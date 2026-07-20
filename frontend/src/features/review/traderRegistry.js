export const TRADER_ID_PATTERN = /^[a-z][a-z0-9_]{1,63}$/;
export const TRADER_COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/;

const SERVER_FIELDS = new Set(['trader_id', 'display_name', 'color', 'active', 'sort_order']);

function tradersOf(registry) {
  return Array.isArray(registry?.traders) ? registry.traders : [];
}

export function nextTraderSortOrder(registry) {
  const used = new Set(
    tradersOf(registry)
      .map((trader) => Number(trader.sort_order))
      .filter((value) => Number.isInteger(value) && value >= 0),
  );
  let candidate = 10;
  while (used.has(candidate)) candidate += 10;
  return candidate;
}

export function createTraderDraft(registry) {
  return {
    trader_id: '',
    display_name: '',
    color: '',
    active: true,
    sort_order: String(nextTraderSortOrder(registry)),
  };
}

export function normalizeTraderDraft(draft) {
  return {
    trader_id: String(draft?.trader_id ?? '').trim(),
    display_name: String(draft?.display_name ?? '').trim(),
    color: String(draft?.color ?? '').trim(),
    active: draft?.active,
    sort_order: typeof draft?.sort_order === 'string' ? draft.sort_order.trim() : draft?.sort_order,
  };
}

export function validateTraderDraft(draft, registry) {
  const value = normalizeTraderDraft(draft);
  const traders = tradersOf(registry);
  const errors = {};

  if (!TRADER_ID_PATTERN.test(value.trader_id)) {
    errors.trader_id = '请输入 2–64 位小写 trader_id：字母开头，仅含小写字母、数字或下划线。';
  } else if (traders.some((trader) => trader.trader_id === value.trader_id)) {
    errors.trader_id = 'trader_id 已存在。';
  }

  if (!value.display_name) errors.display_name = 'Display name 不能为空。';

  if (!TRADER_COLOR_PATTERN.test(value.color)) {
    errors.color = 'Color 必须是带 # 的六位十六进制颜色。';
  } else if (traders.some((trader) => String(trader.color).toLowerCase() === value.color.toLowerCase())) {
    errors.color = 'Color 必须与现有交易者不同。';
  }

  if (typeof value.active !== 'boolean') errors.active = 'Active 必须是布尔值。';

  const orderText = String(value.sort_order ?? '');
  if (!/^\d+$/.test(orderText) || !Number.isSafeInteger(Number(orderText))) {
    errors.sort_order = 'Sort order 必须是非负整数。';
  } else if (traders.some((trader) => Number(trader.sort_order) === Number(orderText))) {
    errors.sort_order = 'Sort order 必须唯一。';
  }

  return errors;
}

export function appendTraderDraft(registry, draft) {
  const fieldErrors = validateTraderDraft(draft, registry);
  if (Object.keys(fieldErrors).length) return { registry, trader: null, fieldErrors };

  const value = normalizeTraderDraft(draft);
  const trader = {
    trader_id: value.trader_id,
    display_name: value.display_name,
    color: value.color,
    active: value.active,
    sort_order: Number(value.sort_order),
  };
  return {
    registry: { ...registry, traders: [...tradersOf(registry), trader] },
    trader,
    fieldErrors: {},
  };
}

export function removeUnsavedTrader(registry, index) {
  return {
    ...registry,
    traders: tradersOf(registry).filter((_, traderIndex) => traderIndex !== index),
  };
}

export function associateRegistryServerError(errorBody, { rowCount = 0, controlPaths = null } = {}) {
  const raw = String(errorBody ?? '').trim();
  let message = raw || '保存注册表失败。';
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed?.detail === 'string' && parsed.detail.trim()) message = parsed.detail.trim();
  } catch (_) {
    // The API client also carries plain response text in Error.message.
  }

  const match = message.match(/registry\.traders\[(\d+)\]\.([a-z_][a-z0-9_]*)/i);
  if (!match) return { message, rowIndex: null, field: null, fieldPath: null };

  const rowIndex = Number(match[1]);
  const field = match[2];
  const fieldPath = `${rowIndex}.${field}`;
  if (
    !Number.isInteger(rowIndex)
    || rowIndex < 0
    || rowIndex >= rowCount
    || !SERVER_FIELDS.has(field)
    || (controlPaths && !controlPaths.has(fieldPath))
  ) {
    return { message, rowIndex: null, field: null, fieldPath: null };
  }
  return { message, rowIndex, field, fieldPath };
}
