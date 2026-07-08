export const API_KEY_STORAGE_KEY = "quant_gemini_api_key";
export const API_KEY_HEADER = "X-Gemini-Api-Key";

export function getStoredApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(API_KEY_STORAGE_KEY);
}

export function setStoredApiKey(key: string): void {
  localStorage.setItem(API_KEY_STORAGE_KEY, key.trim());
}

export function clearStoredApiKey(): void {
  localStorage.removeItem(API_KEY_STORAGE_KEY);
}

export function maskApiKey(key: string): string {
  if (key.length <= 8) return "••••••••";
  return `${key.slice(0, 4)}••••${key.slice(-4)}`;
}

export function hasApiKey(): boolean {
  const key = getStoredApiKey();
  return Boolean(key && key.trim().length > 0);
}
