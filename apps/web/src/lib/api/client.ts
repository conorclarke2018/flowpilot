const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `Request failed with status ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; params?: Record<string, string> } = {},
): Promise<T> {
  const url = new URL(`${API_BASE_URL}/api/v1${path}`);
  for (const [key, value] of Object.entries(options.params ?? {})) {
    url.searchParams.set(key, value);
  }

  const response = await fetch(url.toString(), {
    method: options.method ?? "GET",
    headers: options.body ? { "Content-Type": "application/json" } : undefined,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new ApiError(response.status, detail?.detail ?? detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const apiClient = {
  get: <T>(path: string, params?: Record<string, string>) => request<T>(path, { params }),
  post: <T>(path: string, body?: unknown, params?: Record<string, string>) =>
    request<T>(path, { method: "POST", body, params }),
  put: <T>(path: string, body?: unknown, params?: Record<string, string>) =>
    request<T>(path, { method: "PUT", body, params }),
  delete: <T>(path: string, params?: Record<string, string>) =>
    request<T>(path, { method: "DELETE", params }),
};
