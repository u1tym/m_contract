<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCategories, fetchContracts } from '../api/contract'
import type { Category, ContractGroup, ContractSummary } from '../types/contract'

const router = useRouter()

const items = ref<ContractSummary[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const error = ref('')
const page = ref(1)
const totalPages = ref(0)
const total = ref(0)

const group = ref<ContractGroup | ''>('')
const asOfDate = ref('')
const categoryId = ref<number | ''>('')
const keyword = ref('')
const includeDeleted = ref(false)
const showFilters = ref(false)

const statusLabel: Record<string, string> = {
  active: '契約中',
  suspended: '一時停止',
  cancelled: '解約済み',
  pending: '手続き中',
}

const loadCategories = async (): Promise<void> => {
  const res = await fetchCategories()
  categories.value = res.items
}

const loadContracts = async (): Promise<void> => {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchContracts({
      page: page.value,
      per_page: 20,
      category_id: categoryId.value === '' ? undefined : Number(categoryId.value),
      q: keyword.value || undefined,
      group: group.value || undefined,
      as_of_date: asOfDate.value || undefined,
      include_deleted: includeDeleted.value || undefined,
      sort: 'updated_at_desc',
    })
    items.value = res.items
    totalPages.value = res.total_pages
    total.value = res.total
  } catch (e) {
    error.value = e instanceof Error ? e.message : '取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const setGroup = (g: ContractGroup | ''): void => {
  group.value = g
  if (g) asOfDate.value = ''
  page.value = 1
  void loadContracts()
}

const applyFilters = (): void => {
  page.value = 1
  void loadContracts()
}

const goPage = (p: number): void => {
  page.value = p
  void loadContracts()
}

onMounted(async () => {
  try {
    await loadCategories()
    await loadContracts()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '初期化に失敗しました'
  }
})

watch(includeDeleted, () => {
  page.value = 1
  void loadContracts()
})

const hasActiveFilters = (): boolean =>
  group.value !== '' ||
  asOfDate.value !== '' ||
  categoryId.value !== '' ||
  keyword.value !== '' ||
  includeDeleted.value
</script>

<template>
  <div>
    <div class="list-toolbar">
      <p v-if="loading" class="meta list-toolbar-count">読み込み中...</p>
      <p v-else class="meta list-toolbar-count">{{ total }} 件</p>
      <button
        type="button"
        class="btn btn-secondary btn-sm filter-toggle"
        :class="{ active: showFilters || hasActiveFilters() }"
        @click="showFilters = !showFilters"
      >
        {{ showFilters ? '検索条件を隠す' : '検索条件' }}
        <span v-if="!showFilters && hasActiveFilters()" class="filter-dot" aria-hidden="true" />
      </button>
    </div>

    <div v-show="showFilters" class="filters card">
      <div class="tab-row">
        <button type="button" class="tab" :class="{ active: group === '' && !asOfDate }" @click="setGroup('')">
          すべて
        </button>
        <button type="button" class="tab" :class="{ active: group === 'active' }" @click="setGroup('active')">
          契約中
        </button>
        <button type="button" class="tab" :class="{ active: group === 'ended' }" @click="setGroup('ended')">
          終了
        </button>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="as-of-date">指定日時点で契約中</label>
          <input id="as-of-date" v-model="asOfDate" type="date" @change="applyFilters" />
        </div>
        <div class="form-group">
          <label for="category">カテゴリ</label>
          <select id="category" v-model="categoryId" @change="applyFilters">
            <option value="">すべて</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label for="keyword">キーワード（会社名・契約名・契約番号）</label>
        <input
          id="keyword"
          v-model="keyword"
          type="search"
          placeholder="検索..."
          @keyup.enter="applyFilters"
        />
      </div>

      <label class="meta" style="display: flex; align-items: center; gap: 8px">
        <input v-model="includeDeleted" type="checkbox" />
        削除済みを含める
      </label>

      <div class="filter-actions">
        <button type="button" class="btn btn-block" @click="applyFilters">検索</button>
        <button type="button" class="btn btn-secondary btn-block" @click="showFilters = false">閉じる</button>
      </div>
    </div>

    <p v-if="error" class="error-box">{{ error }}</p>

    <div v-if="!loading && items.length === 0" class="empty">契約がありません</div>

    <article
      v-for="item in items"
      :key="item.id"
      class="card contract-row"
      :class="{ deleted: item.is_deleted }"
      @click="router.push(`/contracts/${item.id}`)"
    >
      <div class="contract-row-main">
        <div class="contract-row-text">
          <h3>{{ item.provider_name }}</h3>
          <p class="contract-row-sub meta">
            <span v-if="item.contract_name">{{ item.contract_name }}</span>
            <span v-if="item.contract_name && item.category.name"> · </span>
            <span>{{ item.category.name }}</span>
          </p>
        </div>
        <div class="contract-row-side">
          <span v-if="item.is_deleted" class="badge badge-deleted">削除済</span>
          <span v-else-if="item.status === 'cancelled' || (item.end_date && item.end_date < new Date().toISOString().slice(0, 10))" class="badge badge-ended">終了</span>
          <span v-else class="badge badge-active">{{ statusLabel[item.status] || item.status }}</span>
          <span v-if="item.amount" class="contract-row-amount meta">¥{{ item.monthly_amount }}/月</span>
        </div>
      </div>
    </article>

    <div v-if="totalPages > 1" class="pagination">
      <button type="button" class="btn btn-secondary btn-sm" :disabled="page <= 1" @click="goPage(page - 1)">
        前へ
      </button>
      <span class="meta">{{ page }} / {{ totalPages }}</span>
      <button
        type="button"
        class="btn btn-secondary btn-sm"
        :disabled="page >= totalPages"
        @click="goPage(page + 1)"
      >
        次へ
      </button>
    </div>

    <button type="button" class="fab" title="新規契約" aria-label="新規契約" @click="router.push('/contracts/new')">
      <span class="fab-icon">+</span>
    </button>
  </div>
</template>
