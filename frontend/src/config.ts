const trimSlash = (url: string): string => url.trim().replace(/\/$/, '')

/** デバッグモード（セッション延長をスキップ） */
export const isDebug = (): boolean => import.meta.env.VITE_DEBUG === 'true'

/** 契約 API の基点 */
export const getContractApiBase = (): string => {
  if (import.meta.env.DEV) {
    return '/api/contract'
  }
  return trimSlash(import.meta.env.VITE_CONTRACT_ORIGIN || '')
}

/** 認証 API の基点（POST /refresh） */
export const getLoginApiBase = (): string => {
  if (import.meta.env.DEV) {
    return '/api/auth'
  }
  return trimSlash(import.meta.env.VITE_LOGIN_ORIGIN || '')
}
