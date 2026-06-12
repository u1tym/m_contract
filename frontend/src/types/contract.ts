export type ContractStatus = 'active' | 'suspended' | 'cancelled' | 'pending'
export type ContractGroup = 'active' | 'ended' | 'all'
export type PaymentCycle = 'monthly' | 'yearly' | 'quarterly' | 'biannual' | 'one_time' | 'other'
export type CredentialType =
  | 'login_id'
  | 'password'
  | 'pin'
  | 'customer_number'
  | 'email'
  | 'phone'
  | 'api_key'
  | 'other'
export type ContactType = 'phone' | 'email' | 'url' | 'address' | 'other'

export interface Category {
  id: number
  name: string
  icon: string | null
  sort_order: number
}

export interface CategoryBrief {
  id: number
  name: string
  icon: string | null
}

export interface Payment {
  amount: string | null
  currency: string
  payment_cycle: string | null
  payment_day: number | null
  payment_method: string | null
  is_tax_included: boolean
  payment_notes: string | null
}

export interface Credential {
  id: number
  credential_type: CredentialType
  label: string | null
  value: string
  is_masked?: boolean
  url: string | null
  notes: string | null
  sort_order: number
}

export interface Contact {
  id: number
  contact_type: ContactType
  label: string | null
  value: string
  notes: string | null
  sort_order: number
}

export interface Attachment {
  id: number
  file_name: string
  content_type: string | null
  file_size: number
  description: string | null
  sort_order: number
  created_at: string
}

export interface ContractSummary {
  id: number
  category: CategoryBrief
  provider_name: string
  contract_name: string | null
  status: ContractStatus
  start_date: string | null
  end_date: string | null
  amount: string | null
  payment_cycle: string | null
  monthly_amount: string
  credential_count: number
  attachment_count: number
  is_deleted: boolean
  updated_at: string
}

export interface ContractDetail {
  id: number
  category_id: number
  category: CategoryBrief
  provider_name: string
  contract_name: string | null
  contract_number: string | null
  status: ContractStatus
  start_date: string | null
  end_date: string | null
  renewal_date: string | null
  auto_renewal: boolean
  notes: string | null
  payment: Payment
  credentials: Credential[]
  contacts: Contact[]
  attachments: Attachment[]
  is_deleted: boolean
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface ItemsResponse<T> {
  items: T[]
}

export interface ContractListParams {
  page?: number
  per_page?: number
  status?: string
  category_id?: number
  q?: string
  sort?: string
  group?: ContractGroup
  as_of_date?: string
  include_deleted?: boolean
}

export interface ContractCreatePayload {
  category_id: number
  provider_name: string
  contract_name?: string | null
  contract_number?: string | null
  status?: ContractStatus
  start_date?: string | null
  end_date?: string | null
  renewal_date?: string | null
  auto_renewal?: boolean
  notes?: string | null
  payment?: Partial<Payment> | null
  credentials?: Array<{
    credential_type: CredentialType
    label?: string | null
    value: string
    url?: string | null
    notes?: string | null
    sort_order?: number
  }>
  contacts?: Array<{
    contact_type: ContactType
    label?: string | null
    value: string
    notes?: string | null
    sort_order?: number
  }>
}

export type ContractUpdatePayload = Partial<ContractCreatePayload>
