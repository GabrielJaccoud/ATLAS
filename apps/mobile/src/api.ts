export type AtlasConfig = {
  baseUrl: string;
  token: string;
};

export function loadConfig(): AtlasConfig {
  return {
    baseUrl: localStorage.getItem("atlas.baseUrl") || import.meta.env.VITE_ATLAS_API_URL || "http://localhost:8000",
    token: localStorage.getItem("atlas.token") || "",
  };
}

export function saveConfig(config: AtlasConfig) {
  localStorage.setItem("atlas.baseUrl", config.baseUrl.replace(/\/$/, ""));
  localStorage.setItem("atlas.token", config.token);
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
