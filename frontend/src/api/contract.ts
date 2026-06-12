import type {
  Attachment,
  Category,
  Contact,
  ContractCreatePayload,
  ContractDetail,
  ContractListParams,
  ContractSummary,
  ContractUpdatePayload,
  Credential,
  ItemsResponse,
  Paginated,
} from '../types/contract'
import { refreshAccessToken } from '../auth'
import { getContractApiBase, isDebug } from '../config'
import { contractRequest } from './client'

// --- Categories ---

export const fetchCategories = (): Promise<ItemsResponse<Category>> =>
  contractRequest('/categories')

export const createCategory = (body: {
  name: string
  icon?: string | null
  sort_order?: number
}): Promise<Category> =>
  contractRequest('/categories', { method: 'POST', body: JSON.stringify(body) })

export const updateCategory = (
  id: number,
  body: { name?: string; icon?: string | null; sort_order?: number },
): Promise<Category> =>
  contractRequest(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(body) })

export const deleteCategory = (id: number): Promise<void> =>
  contractRequest(`/categories/${id}`, { method: 'DELETE' })

// --- Contracts ---

export const fetchContracts = (
  params: ContractListParams,
): Promise<Paginated<ContractSummary>> =>
  contractRequest('/contracts', undefined, params as Record<string, string | number | boolean | undefined>)

export const fetchContract = (
  id: number,
  includeDeleted = false,
): Promise<ContractDetail> =>
  contractRequest(`/contracts/${id}`, undefined, { include_deleted: includeDeleted || undefined })

export const createContract = (body: ContractCreatePayload): Promise<ContractDetail> =>
  contractRequest('/contracts', { method: 'POST', body: JSON.stringify(body) })

export const updateContract = (id: number, body: ContractUpdatePayload): Promise<ContractDetail> =>
  contractRequest(`/contracts/${id}`, { method: 'PUT', body: JSON.stringify(body) })

export const deleteContract = (id: number): Promise<void> =>
  contractRequest(`/contracts/${id}`, { method: 'DELETE' })

export const restoreContract = (id: number): Promise<ContractDetail> =>
  contractRequest(`/contracts/${id}/restore`, { method: 'POST' })

// --- Credentials ---

export const fetchCredentials = (contractId: number): Promise<ItemsResponse<Credential>> =>
  contractRequest(`/contracts/${contractId}/credentials`)

export const createCredential = (
  contractId: number,
  body: Record<string, unknown>,
): Promise<Credential> =>
  contractRequest(`/contracts/${contractId}/credentials`, {
    method: 'POST',
    body: JSON.stringify(body),
  })

export const updateCredential = (
  contractId: number,
  credentialId: number,
  body: Record<string, unknown>,
): Promise<Credential> =>
  contractRequest(`/contracts/${contractId}/credentials/${credentialId}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })

export const deleteCredential = (contractId: number, credentialId: number): Promise<void> =>
  contractRequest(`/contracts/${contractId}/credentials/${credentialId}`, { method: 'DELETE' })

export const revealCredential = (
  contractId: number,
  credentialId: number,
): Promise<{ id: number; credential_type: string; label: string | null; value: string }> =>
  contractRequest(`/contracts/${contractId}/credentials/${credentialId}/reveal`)

// --- Contacts ---

export const fetchContacts = (contractId: number): Promise<ItemsResponse<Contact>> =>
  contractRequest(`/contracts/${contractId}/contacts`)

export const createContact = (
  contractId: number,
  body: Record<string, unknown>,
): Promise<Contact> =>
  contractRequest(`/contracts/${contractId}/contacts`, {
    method: 'POST',
    body: JSON.stringify(body),
  })

export const updateContact = (
  contractId: number,
  contactId: number,
  body: Record<string, unknown>,
): Promise<Contact> =>
  contractRequest(`/contracts/${contractId}/contacts/${contactId}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })

export const deleteContact = (contractId: number, contactId: number): Promise<void> =>
  contractRequest(`/contracts/${contractId}/contacts/${contactId}`, { method: 'DELETE' })

// --- Attachments ---

export const fetchAttachments = (contractId: number): Promise<ItemsResponse<Attachment>> =>
  contractRequest(`/contracts/${contractId}/attachments`)

export const uploadAttachment = async (
  contractId: number,
  file: File,
  description?: string,
  sortOrder = 0,
): Promise<Attachment> => {
  if (!isDebug()) {
    await refreshAccessToken()
  }
  const form = new FormData()
  form.append('file', file)
  if (description) form.append('description', description)
  form.append('sort_order', String(sortOrder))

  const response = await fetch(`${getContractApiBase()}/contracts/${contractId}/attachments`, {
    method: 'POST',
    credentials: 'include',
    body: form,
  })
  if (!response.ok) {
    throw new Error(`アップロード失敗: HTTP ${response.status}`)
  }
  return (await response.json()) as Attachment
}

export const updateAttachment = (
  contractId: number,
  attachmentId: number,
  body: { description?: string | null; sort_order?: number },
): Promise<Attachment> =>
  contractRequest(`/contracts/${contractId}/attachments/${attachmentId}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })

export const deleteAttachment = (contractId: number, attachmentId: number): Promise<void> =>
  contractRequest(`/contracts/${contractId}/attachments/${attachmentId}`, { method: 'DELETE' })

export const downloadAttachmentUrl = (contractId: number, attachmentId: number): string =>
  `${getContractApiBase()}/contracts/${contractId}/attachments/${attachmentId}/download`
