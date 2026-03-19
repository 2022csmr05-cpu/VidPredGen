const STORAGE_KEYS = {
  USER: 'videoai_user',
  HISTORY: 'videoai_history',
  SESSION: 'videoai_session',
  OUTPUT: 'videoai_output',
};

const ONE_DAY_MS = 24 * 60 * 60 * 1000;

export function setItem(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getItem(key) {
  const raw = localStorage.getItem(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function removeItem(key) {
  localStorage.removeItem(key);
}

export function getUser() {
  return getItem(STORAGE_KEYS.USER);
}

export function setUser(user) {
  setItem(STORAGE_KEYS.USER, user);
}

export function removeUser() {
  removeItem(STORAGE_KEYS.USER);
}

export function getHistory() {
  const history = getItem(STORAGE_KEYS.HISTORY);
  if (!Array.isArray(history)) return [];
  return history;
}

export function addHistory(entry) {
  const history = getHistory();
  history.unshift(entry);
  setItem(STORAGE_KEYS.HISTORY, history);
}

export function clearHistory() {
  removeItem(STORAGE_KEYS.HISTORY);
}

export function cleanupExpiredHistory() {
  const now = Date.now();
  const history = getHistory();
  const fresh = history.filter((item) => {
    if (!item?.createdAt) return false;
    return now - item.createdAt < ONE_DAY_MS;
  });
  setItem(STORAGE_KEYS.HISTORY, fresh);
}

export function getSession() {
  return getItem(STORAGE_KEYS.SESSION);
}

export function setSession(session) {
  setItem(STORAGE_KEYS.SESSION, { ...session, updatedAt: Date.now() });
}

export function removeSession() {
  removeItem(STORAGE_KEYS.SESSION);
}

export function clearAll() {
  Object.values(STORAGE_KEYS).forEach((key) => removeItem(key));
}

export function formatTimestamp(timestamp) {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString();
  } catch {
    return '';
  }
}
