import { refreshAccessToken } from '../auth'
import { getContractApiBase, isDebug } from '../config'

const toQuery = (params: Record<string, string | number | boolean | undefined>): string => {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '' && value !== false) {
      query.set(key, String(value))
    }
  })
  const qs = query.toString()
  return qs ? `?${qs}` : ''
}

export const contractRequest = async <T>(
  path: string,
  init?: RequestInit,
  query?: Record<string, string | number | boolean | undefined>,
): Promise<T> => {
  if (!isDebug()) {
    await refreshAccessToken()
  }

  const qs = query ? toQuery(query) : ''
  const url = `${getContractApiBase()}${path}${qs}`
  const isFormData = init?.body instanceof FormData

  const response = await fetch(url, {
    credentials: 'include',
    ...init,
    headers: isFormData
      ? { ...(init?.headers || {}) }
      : {
          'Content-Type': 'application/json',
          ...(init?.headers || {}),
        },
  })

  if (!response.ok) {
    let message = `HTTP ${response.status}`
    try {
      const data = (await response.json()) as { detail?: string; code?: string }
      if (data.detail) {
        message = typeof data.detail === 'string' ? data.detail : message
      }
    } catch {
      // ignore
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export { toQuery }
