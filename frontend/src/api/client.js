const API_BASE = import.meta.env.VITE_API_BASE || '/api';
const TOKEN_KEY = 'tangStrategy:token';
const ROLE_KEY = 'tangStrategy:role';

export function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getRole() {
  return window.localStorage.getItem(ROLE_KEY);
}

export function clearSession() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(ROLE_KEY);
}

export async function login(password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) throw new Error('Password rejected');
  const data = await response.json();
  window.localStorage.setItem(TOKEN_KEY, data.token);
  window.localStorage.setItem(ROLE_KEY, data.role);
  return data;
}

export async function api(path, options = {}) {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (response.status === 401) {
    clearSession();
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const Api = {
  tickers: () => api('/tickers'),
  marketDays: (params = {}) => api(`/market-days?${new URLSearchParams(params)}`),
  bars: (id, timeframe) => api(`/market-days/${id}/bars?timeframe=${timeframe}`),
  strategies: () => api('/strategies'),
  review: (marketDayId, strategyId) => api(`/reviews/assemble?market_day_id=${marketDayId}&strategy_id=${strategyId}`),
  strategy: (id) => api(`/strategies/${id}`),
  teaching: (type) => api(`/teaching/${type}`),
  tradeRecords: (params = {}) => api(`/trade-records?${new URLSearchParams(params)}`),
  saveTraders: (payload) => api('/admin/traders', { method: 'PUT', body: JSON.stringify(payload) }),
  saveTradeRecords: (payload) => api('/admin/trade-records', { method: 'PUT', body: JSON.stringify(payload) }),
  importSeed: () => api('/admin/import/seed', { method: 'POST' }),
};
