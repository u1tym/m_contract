import { createRouter, createWebHashHistory } from 'vue-router'
import ContractListView from '../views/ContractListView.vue'
import ContractDetailView from '../views/ContractDetailView.vue'
import ContractFormView from '../views/ContractFormView.vue'
import CategoryListView from '../views/CategoryListView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/contracts' },
    { path: '/contracts', name: 'contracts', component: ContractListView },
    { path: '/contracts/new', name: 'contract-new', component: ContractFormView },
    { path: '/contracts/:id', name: 'contract-detail', component: ContractDetailView, props: true },
    { path: '/contracts/:id/edit', name: 'contract-edit', component: ContractFormView, props: true },
    { path: '/categories', name: 'categories', component: CategoryListView },
  ],
})

export default router
