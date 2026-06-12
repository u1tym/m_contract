<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createContract, fetchCategories, fetchContract, updateContract } from '../api/contract'
import type { Category, ContractStatus, PaymentCycle } from '../types/contract'

const props = defineProps<{ id?: string }>()
const route = useRoute()
const router = useRouter()

const isEdit = computed(() => Boolean(props.id || route.params.id))
const contractId = computed(() => Number(props.id || route.params.id || 0))

const categories = ref<Category[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')

const categoryId = ref<number | ''>('')
const providerName = ref('')
const contractName = ref('')
const contractNumber = ref('')
const status = ref<ContractStatus>('active')
const startDate = ref('')
const endDate = ref('')
const renewalDate = ref('')
const autoRenewal = ref(true)
const notes = ref('')

const amount = ref('')
const paymentCycle = ref<PaymentCycle>('monthly')
const paymentDay = ref<number | ''>('')
const paymentMethod = ref('')
const isTaxIncluded = ref(true)
const paymentNotes = ref('')

const paymentCycles: { value: PaymentCycle; label: string }[] = [
  { value: 'monthly', label: '月額' },
  { value: 'yearly', label: '年額' },
  { value: 'quarterly', label: '四半期' },
  { value: 'biannual', label: '半年' },
  { value: 'one_time', label: '一括' },
  { value: 'other', label: 'その他' },
]

const load = async (): Promise<void> => {
  loading.value = true
  error.value = ''
  try {
    const catRes = await fetchCategories()
    categories.value = catRes.items

    if (isEdit.value) {
      const c = await fetchContract(contractId.value)
      categoryId.value = c.category_id
      providerName.value = c.provider_name
      contractName.value = c.contract_name || ''
      contractNumber.value = c.contract_number || ''
      status.value = c.status
      startDate.value = c.start_date || ''
      endDate.value = c.end_date || ''
      renewalDate.value = c.renewal_date || ''
      autoRenewal.value = c.auto_renewal
      notes.value = c.notes || ''
      amount.value = c.payment.amount || ''
      paymentCycle.value = (c.payment.payment_cycle as PaymentCycle) || 'monthly'
      paymentDay.value = c.payment.payment_day ?? ''
      paymentMethod.value = c.payment.payment_method || ''
      isTaxIncluded.value = c.payment.is_tax_included
      paymentNotes.value = c.payment.payment_notes || ''
    } else if (categories.value.length > 0) {
      categoryId.value = categories.value[0].id
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
}

const buildPayload = () => ({
  category_id: Number(categoryId.value),
  provider_name: providerName.value,
  contract_name: contractName.value || null,
  contract_number: contractNumber.value || null,
  status: status.value,
  start_date: startDate.value || null,
  end_date: endDate.value || null,
  renewal_date: renewalDate.value || null,
  auto_renewal: autoRenewal.value,
  notes: notes.value || null,
  payment: {
    amount: amount.value ? amount.value : null,
    payment_cycle: paymentCycle.value,
    payment_day: paymentDay.value === '' ? null : Number(paymentDay.value),
    payment_method: paymentMethod.value || null,
    is_tax_included: isTaxIncluded.value,
    payment_notes: paymentNotes.value || null,
  },
})

const save = async (): Promise<void> => {
  if (!providerName.value || categoryId.value === '') {
    error.value = '会社名とカテゴリは必須です'
    return
  }
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      const updated = await updateContract(contractId.value, buildPayload())
      router.push(`/contracts/${updated.id}`)
    } else {
      const created = await createContract(buildPayload())
      router.push(`/contracts/${created.id}`)
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div>
    <button type="button" class="btn btn-secondary btn-sm" @click="router.back()">← 戻る</button>
    <h2 style="margin: 16px 0">{{ isEdit ? '契約を編集' : '契約を追加' }}</h2>

    <p v-if="error" class="error-box">{{ error }}</p>
    <p v-if="loading" class="meta">読み込み中...</p>

    <form v-else class="card" @submit.prevent="save">
      <div class="form-group">
        <label for="category">カテゴリ *</label>
        <select id="category" v-model="categoryId" required>
          <option value="" disabled>選択してください</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="provider">会社名 *</label>
        <input id="provider" v-model="providerName" required maxlength="200" />
      </div>

      <div class="form-group">
        <label for="contract-name">プラン名・契約名</label>
        <input id="contract-name" v-model="contractName" maxlength="200" />
      </div>

      <div class="form-group">
        <label for="contract-number">契約番号</label>
        <input id="contract-number" v-model="contractNumber" maxlength="100" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="status">状態</label>
          <select id="status" v-model="status">
            <option value="active">契約中</option>
            <option value="suspended">一時停止</option>
            <option value="cancelled">解約済み</option>
            <option value="pending">手続き中</option>
          </select>
        </div>
        <div class="form-group">
          <label>
            <input v-model="autoRenewal" type="checkbox" />
            自動更新
          </label>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="start">開始日</label>
          <input id="start" v-model="startDate" type="date" />
        </div>
        <div class="form-group">
          <label for="end">終了日</label>
          <input id="end" v-model="endDate" type="date" />
        </div>
      </div>

      <div class="form-group">
        <label for="renewal">更新日</label>
        <input id="renewal" v-model="renewalDate" type="date" />
      </div>

      <h3 class="section-title">支払い</h3>
      <div class="form-row">
        <div class="form-group">
          <label for="amount">金額</label>
          <input id="amount" v-model="amount" type="number" min="0" step="1" />
        </div>
        <div class="form-group">
          <label for="cycle">周期</label>
          <select id="cycle" v-model="paymentCycle">
            <option v-for="p in paymentCycles" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="pay-day">支払日</label>
          <input id="pay-day" v-model="paymentDay" type="number" min="1" max="31" />
        </div>
        <div class="form-group">
          <label for="pay-method">支払い方法</label>
          <input id="pay-method" v-model="paymentMethod" />
        </div>
      </div>

      <div class="form-group">
        <label>
          <input v-model="isTaxIncluded" type="checkbox" />
          税込
        </label>
      </div>

      <div class="form-group">
        <label for="pay-notes">支払い備考</label>
        <textarea id="pay-notes" v-model="paymentNotes" rows="2" />
      </div>

      <div class="form-group">
        <label for="notes">メモ</label>
        <textarea id="notes" v-model="notes" rows="3" />
      </div>

      <p v-if="!isEdit" class="meta">
        認証情報・連絡先・契約書ファイルは、作成後に詳細画面から追加できます。
      </p>

      <button type="submit" class="btn btn-block" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </form>
  </div>
</template>
