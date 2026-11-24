export type AtlasConfig = {
  baseUrl: string;
  token: string;
};

const DEFAULT_API = import.meta.env.VITE_ATLAS_API_URL || "https://atlas-18-api.onrender.com";

export function loadConfig(): AtlasConfig {
  return {
    baseUrl: localStorage.getItem("atlas.baseUrl") || DEFAULT_API,
    token: localStorage.getItem("atlas.token") || "",
  };
}

export function saveConfig(config: AtlasConfig) {
  localStorage.setItem("atlas.baseUrl", config.baseUrl.replace(/\/$/, ""));
  localStorage.setItem("atlas.token", config.token);
}

export function clearSession() {
  localStorage.removeItem("atlas.token");
}

export async function pairOwner(code: string): Promise<{ token: string; expires_in_days: number }> {
  const config = loadConfig();
  const response = await fetch(`${config.baseUrl}/auth/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!response.ok) {
    throw new Error("Código de proprietário inválido ou API indisponível.");
  }
  const data = await response.json();
  saveConfig({ ...config, token: data.token });
  return data;
}

export async function refreshSession(): Promise<void> {
  const config = loadConfig();
  if (!config.token) throw new Error("Este navegador ainda não está pareado.");
  const response = await fetch(`${config.baseUrl}/auth/refresh`, {
    method: "POST",
    headers: { Authorization: `Bearer ${config.token}` },
  });
  if (!response.ok) {
    if (response.status === 401) clearSession();
    throw new Error(`${response.status} ${response.statusText}`);
  }
  const data = await response.json();
  saveConfig({ ...config, token: data.token });
}

export async function atlasFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const config = loadConfig();
  const headers = new Headers(init.headers || {});
  if (config.token) headers.set("Authorization", `Bearer ${config.token}`);
  if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`${config.baseUrl}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }
  return response.json();
}
