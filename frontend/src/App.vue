<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { getLoginMenuUrl } from './config'

const loginMenuUrl = getLoginMenuUrl()
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="app-header-start">
        <a :href="loginMenuUrl" class="btn btn-secondary btn-sm">← 戻る</a>
        <h1>契約管理</h1>
      </div>
      <nav class="app-nav">
        <RouterLink to="/contracts">契約</RouterLink>
        <RouterLink to="/categories">カテゴリ</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>
