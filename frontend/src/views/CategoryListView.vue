<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { createCategory, deleteCategory, fetchCategories, updateCategory } from '../api/contract'
import type { Category } from '../types/contract'

const items = ref<Category[]>([])
const loading = ref(false)
const error = ref('')

const load = async (): Promise<void> => {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchCategories()
    items.value = res.items
  } catch (e) {
    error.value = e instanceof Error ? e.message : '取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const addCategory = async (): Promise<void> => {
  const name = prompt('カテゴリ名')
  if (!name?.trim()) return
  try {
    await createCategory({ name: name.trim(), sort_order: items.value.length * 10 })
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '作成に失敗しました'
  }
}

const editCategory = async (item: Category): Promise<void> => {
  const name = prompt('カテゴリ名', item.name)
  if (!name?.trim()) return
  try {
    await updateCategory(item.id, { name: name.trim() })
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '更新に失敗しました'
  }
}

const removeCategory = async (item: Category): Promise<void> => {
  if (!confirm(`「${item.name}」を削除しますか？`)) return
  try {
    await deleteCategory(item.id)
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '削除に失敗しました'
  }
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div>
    <h2 style="margin: 0 0 16px">カテゴリ管理</h2>
    <p class="meta">契約の分類に使うカテゴリを自由に登録できます。</p>

    <p v-if="error" class="error-box">{{ error }}</p>
    <p v-if="loading" class="meta">読み込み中...</p>

    <div v-for="item in items" :key="item.id" class="card list-item">
      <div>
        <h3 style="margin: 0">{{ item.name }}</h3>
        <p v-if="item.icon" class="meta">icon: {{ item.icon }}</p>
      </div>
      <div class="actions-row" style="margin: 0">
        <button type="button" class="btn btn-secondary btn-sm" @click="editCategory(item)">編集</button>
        <button type="button" class="btn btn-danger btn-sm" @click="removeCategory(item)">削除</button>
      </div>
    </div>

    <div v-if="!loading && items.length === 0" class="empty">カテゴリがありません</div>

    <button type="button" class="btn btn-block" style="margin-top: 16px" @click="addCategory">
      + カテゴリを追加
    </button>
  </div>
</template>
