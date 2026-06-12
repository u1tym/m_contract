<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>契約管理</h1>
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
