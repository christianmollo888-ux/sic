import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Views (to be created)
const Dashboard = () => import('./views/Dashboard.vue')
const JournalEntries = () => import('./views/JournalEntries.vue')
const DataInspector = () => import('./views/DataInspector.vue')
const Statistics = () => import('./views/Statistics.vue')
const DataDictionary = () => import('./views/DataDictionary.vue')
const ERDiagram = () => import('./views/ERDiagram.vue')
const Reports = () => import('./views/Reports.vue')
const FormUpload = () => import('./views/FormUpload.vue')
const FormHistory = () => import('./views/FormHistory.vue')
const TaxAuditReport = () => import('./views/TaxAuditReport.vue')
const ResumenFormulario200 = () => import('./views/ResumenFormulario200.vue')

const routes = [
  { path: '/', component: Dashboard },
  { path: '/entries', component: JournalEntries },
  { path: '/inspector', component: DataInspector },
  { path: '/statistics', component: Statistics },
  { path: '/dictionary', component: DataDictionary },
  { path: '/diagram', component: ERDiagram },
  { path: '/reports', component: Reports },
  { path: '/forms', component: FormUpload },
  { path: '/form-history', component: FormHistory },
  { path: '/tax-audit', component: TaxAuditReport },
  { path: '/resumen-200', component: ResumenFormulario200 }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
