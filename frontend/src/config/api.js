/**
 * Navi API Client Configuration & Base Constants
 */

const normalizeBaseUrl = (value, fallback) => {
  const normalized = (value || fallback || "").trim();
  return normalized ? normalized.replace(/\/$/, "") : fallback;
};

const apiBaseUrl = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL,
  import.meta.env.DEV ? "http://localhost:8000/api/v1" : "/api/v1"
);

export const API_BASE_URL = apiBaseUrl;
export const WS_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_WS_BASE_URL ||
    (apiBaseUrl.startsWith("https://")
      ? apiBaseUrl.replace("https://", "wss://")
      : apiBaseUrl.startsWith("http://")
        ? apiBaseUrl.replace("http://", "ws://")
        : apiBaseUrl),
  import.meta.env.DEV ? "ws://localhost:8000/api/v1" : "/api/v1"
);
