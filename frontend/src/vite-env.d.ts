/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CONTRACT_ORIGIN: string
  readonly VITE_LOGIN_ORIGIN: string
  readonly VITE_DEBUG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
