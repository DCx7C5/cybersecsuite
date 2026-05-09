export type ApiErrorData = {
  status: number
  message: string
  detail?: unknown
}

export class ApiError extends Error {
  public readonly status: number
  public readonly detail?: unknown

  public constructor({ status, message, detail }: ApiErrorData) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.detail = detail
  }
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").trim().replace(/\/+$/, "")

function resolvePath(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path
  }
  const normalizedPath = path.startsWith("/") ? path : `/${path}`
  return API_BASE_URL ? `${API_BASE_URL}${normalizedPath}` : normalizedPath
}

function hasBody(status: number): boolean {
  return status !== 204 && status !== 205 && status !== 304
}

async function readErrorPayload(response: Response): Promise<unknown> {
  if (!hasBody(response.status)) {
    return undefined
  }

  const contentType = response.headers.get("content-type")?.toLowerCase() ?? ""
  if (contentType.includes("application/json")) {
    try {
      return await response.json()
    } catch {
      return undefined
    }
  }

  try {
    return await response.text()
  } catch {
    return undefined
  }
}

function deriveMessage(response: Response, detail: unknown): string {
  if (typeof detail === "string" && detail.trim()) {
    return detail
  }

  if (detail && typeof detail === "object") {
    const maybeDetail = (detail as { detail?: unknown }).detail
    if (typeof maybeDetail === "string" && maybeDetail.trim()) {
      return maybeDetail
    }
    const maybeMessage = (detail as { message?: unknown }).message
    if (typeof maybeMessage === "string" && maybeMessage.trim()) {
      return maybeMessage
    }
  }

  return response.statusText || "Request failed"
}

async function apiRequest<T>(
  method: "GET" | "POST" | "PUT" | "DELETE",
  path: string,
  body?: unknown,
): Promise<T> {
  const response = await fetch(resolvePath(path), {
    method,
    headers: {
      "content-type": "application/json",
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (!response.ok) {
    const detail = await readErrorPayload(response)
    throw new ApiError({
      status: response.status,
      message: deriveMessage(response, detail),
      detail,
    })
  }

  if (!hasBody(response.status)) {
    return undefined as T
  }

  const contentType = response.headers.get("content-type")?.toLowerCase() ?? ""
  if (!contentType.includes("application/json")) {
    return (await response.text()) as T
  }

  return (await response.json()) as T
}

export function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>("GET", path)
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return apiRequest<T>("POST", path, body)
}

export function apiPut<T>(path: string, body?: unknown): Promise<T> {
  return apiRequest<T>("PUT", path, body)
}

export function apiDelete(path: string): Promise<void> {
  return apiRequest<void>("DELETE", path)
}

export default {
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  ApiError,
  hasBody,
}
