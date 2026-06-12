<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  createContact,
  createCredential,
  deleteAttachment,
  deleteContact,
  deleteContract,
  deleteCredential,
  downloadAttachmentUrl,
  fetchContract,
  restoreContract,
  revealCredential,
  updateContract,
  uploadAttachment,
} from '../api/contract'
import type { ContractDetail } from '../types/contract'

const props = defineProps<{ id: string }>()
const route = useRoute()
const router = useRouter()

const contract = ref<ContractDetail | null>(null)
const loading = ref(true)
const error = ref('')
const message = ref('')

const contractId = computed(() => Number(props.id || route.params.id))

const statusLabel: Record<string, string> = {
  active: '契約中',
  suspended: '一時停止',
  cancelled: '解約済み',
  pending: '手続き中',
}

const load = async (): Promise<void> => {
  loading.value = true
  error.value = ''
  try {
    const includeDeleted = route.query.deleted === '1'
    contract.value = await fetchContract(contractId.value, includeDeleted)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const endContract = async (): Promise<void> => {
  if (!contract.value || !confirm('この契約を終了しますか？（解約済みにします）')) return
  try {
    contract.value = await updateContract(contractId.value, {
      status: 'cancelled',
      end_date: new Date().toISOString().slice(0, 10),
    })
    message.value = '契約を終了しました'
  } catch (e) {
    error.value = e instanceof Error ? e.message : '終了に失敗しました'
  }
}

const removeContract = async (): Promise<void> => {
  if (!confirm('この契約を削除しますか？（論理削除。復元可能）')) return
  try {
    await deleteContract(contractId.value)
    router.push('/contracts')
  } catch (e) {
    error.value = e instanceof Error ? e.message : '削除に失敗しました'
  }
}

const doRestore = async (): Promise<void> => {
  if (!confirm('この契約を復元しますか？')) return
  try {
    contract.value = await restoreContract(contractId.value)
    message.value = '契約を復元しました'
  } catch (e) {
    error.value = e instanceof Error ? e.message : '復元に失敗しました'
  }
}

const showPassword = async (credentialId: number): Promise<void> => {
  try {
    const res = await revealCredential(contractId.value, credentialId)
    alert(`${res.label || res.credential_type}: ${res.value}`)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '表示に失敗しました'
  }
}

const addCredential = async (): Promise<void> => {
  const credentialType = prompt('種別 (login_id, password, pin, ...)', 'login_id')
  if (!credentialType) return
  const value = prompt('値')
  if (!value) return
  try {
    await createCredential(contractId.value, {
      credential_type: credentialType,
      label: prompt('ラベル') || null,
      value,
    })
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '追加に失敗しました'
  }
}

const removeCredential = async (credentialId: number): Promise<void> => {
  if (!confirm('削除しますか？')) return
  await deleteCredential(contractId.value, credentialId)
  await load()
}

const addContact = async (): Promise<void> => {
  const contactType = prompt('種別 (phone, email, url, ...)', 'phone')
  if (!contactType) return
  const value = prompt('値')
  if (!value) return
  try {
    await createContact(contractId.value, {
      contact_type: contactType,
      label: prompt('ラベル') || null,
      value,
    })
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '追加に失敗しました'
  }
}

const removeContact = async (contactId: number): Promise<void> => {
  if (!confirm('削除しますか？')) return
  await deleteContact(contractId.value, contactId)
  await load()
}

const onFileSelect = async (event: Event): Promise<void> => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    await uploadAttachment(contractId.value, file, prompt('説明') || undefined)
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'アップロードに失敗しました'
  } finally {
    input.value = ''
  }
}

const removeAttachment = async (attachmentId: number): Promise<void> => {
  if (!confirm('ファイルを削除しますか？')) return
  await deleteAttachment(contractId.value, attachmentId)
  await load()
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div>
    <button type="button" class="btn btn-secondary btn-sm" @click="router.push('/contracts')">← 一覧</button>

    <p v-if="error" class="error-box">{{ error }}</p>
    <p v-if="message" class="meta" style="color: #166534">{{ message }}</p>
    <p v-if="loading" class="meta">読み込み中...</p>

    <template v-if="contract">
      <div class="card" style="margin-top: 12px">
        <div style="display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap">
          <div>
            <h2 style="margin: 0 0 8px">{{ contract.provider_name }}</h2>
            <p v-if="contract.contract_name" class="meta">{{ contract.contract_name }}</p>
          </div>
          <div>
            <span v-if="contract.is_deleted" class="badge badge-deleted">削除済</span>
            <span v-else class="badge badge-active">{{ statusLabel[contract.status] }}</span>
          </div>
        </div>

        <dl class="meta" style="margin-top: 12px; line-height: 1.8">
          <div>カテゴリ: {{ contract.category.name }}</div>
          <div v-if="contract.contract_number">契約番号: {{ contract.contract_number }}</div>
          <div v-if="contract.start_date">開始: {{ contract.start_date }}</div>
          <div v-if="contract.end_date">終了: {{ contract.end_date }}</div>
          <div v-if="contract.renewal_date">更新日: {{ contract.renewal_date }}</div>
          <div v-if="contract.payment.amount">
            支払い: ¥{{ contract.payment.amount }} / {{ contract.payment.payment_cycle }}
            <span v-if="contract.payment.payment_method">（{{ contract.payment.payment_method }}）</span>
          </div>
          <div v-if="contract.notes">メモ: {{ contract.notes }}</div>
        </dl>

        <div class="actions-row">
          <template v-if="contract.is_deleted">
            <button type="button" class="btn" @click="doRestore">復元</button>
          </template>
          <template v-else>
            <button type="button" class="btn btn-secondary" @click="router.push(`/contracts/${contractId}/edit`)">
              編集
            </button>
            <button
              v-if="contract.status !== 'cancelled'"
              type="button"
              class="btn btn-secondary"
              @click="endContract"
            >
              契約終了
            </button>
            <button type="button" class="btn btn-danger" @click="removeContract">削除</button>
          </template>
        </div>
      </div>

      <template v-if="!contract.is_deleted">
        <h3 class="section-title">認証情報</h3>
        <div v-for="cred in contract.credentials" :key="cred.id" class="card">
          <strong>{{ cred.label || cred.credential_type }}</strong>
          <p class="meta">{{ cred.value }}</p>
          <div class="actions-row">
            <button
              v-if="cred.is_masked"
              type="button"
              class="btn btn-secondary btn-sm"
              @click="showPassword(cred.id)"
            >
              表示
            </button>
            <button type="button" class="btn btn-danger btn-sm" @click="removeCredential(cred.id)">削除</button>
          </div>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" @click="addCredential">+ 認証情報</button>

        <h3 class="section-title">連絡先</h3>
        <div v-for="contact in contract.contacts" :key="contact.id" class="card">
          <strong>{{ contact.label || contact.contact_type }}</strong>
          <p>{{ contact.value }}</p>
          <p v-if="contact.notes" class="meta">{{ contact.notes }}</p>
          <button type="button" class="btn btn-danger btn-sm" @click="removeContact(contact.id)">削除</button>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" @click="addContact">+ 連絡先</button>

        <h3 class="section-title">契約書ファイル</h3>
        <div v-for="att in contract.attachments" :key="att.id" class="card">
          <strong>{{ att.file_name }}</strong>
          <p v-if="att.description" class="meta">{{ att.description }}</p>
          <div class="actions-row">
            <a
              class="btn btn-secondary btn-sm"
              :href="downloadAttachmentUrl(contractId, att.id)"
              target="_blank"
              rel="noopener"
            >
              ダウンロード
            </a>
            <button type="button" class="btn btn-danger btn-sm" @click="removeAttachment(att.id)">削除</button>
          </div>
        </div>
        <label class="btn btn-secondary btn-sm" style="cursor: pointer">
          + ファイル追加
          <input type="file" accept=".pdf,image/jpeg,image/png,image/webp" hidden @change="onFileSelect" />
        </label>
      </template>
    </template>
  </div>
</template>
