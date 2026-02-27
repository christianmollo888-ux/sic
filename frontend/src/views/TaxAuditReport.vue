<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import PageHero from '../components/PageHero.vue'

const report = ref<any>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const taxpayers = ref<any[]>([])
const isFetchingTaxpayers = ref(true)

const nit = ref('')
const year = ref(new Date().getFullYear())
const availableYears = [2022, 2023, 2024, 2025, 2026]

const fetchTaxpayers = async () => {
  isFetchingTaxpayers.value = true
  try {
    const resp = await axios.get('http://localhost:8000/forms/taxpayers')
    taxpayers.value = resp.data
    if (taxpayers.value.length > 0) nit.value = taxpayers.value[0].nit
  } catch (e: any) { console.error("Error fetching taxpayers:", e) }
  finally { isFetchingTaxpayers.value = false }
}

const fetchReport = async () => {
  if (!nit.value) return
  isLoading.value = true; error.value = null
  try {
    const resp = await axios.get(`http://localhost:8000/forms/reports/tax-audit?nit=${nit.value}&year=${year.value}`)
    report.value = resp.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al cargar el reporte'
    report.value = null
  } finally { isLoading.value = false }
}

const downloadExcel = () => { if (nit.value && report.value) window.open(`http://localhost:8000/forms/reports/tax-audit/excel?nit=${nit.value}&year=${year.value}`) }
const downloadPdf   = () => { if (nit.value && report.value) window.open(`http://localhost:8000/forms/reports/tax-audit/pdf?nit=${nit.value}&year=${year.value}`) }
const formatCurrency = (val: number) => new Intl.NumberFormat('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)
const formatDate = (d: string | null) => d ? new Date(d).toLocaleDateString('es-BO') : '-'

onMounted(async () => { await fetchTaxpayers(); if (nit.value) fetchReport() })

const months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

const getGroupedRows = () => {
  if (!report.value) return []
  const groups: Record<string, any[]> = {}
  report.value.rows.forEach((row: any) => {
    if (!groups[row.rubric]) groups[row.rubric] = []
    groups[row.rubric].push(row)
  })
  return Object.entries(groups).map(([name, rows]) => ({ name, rows }))
}
</script>

<template>
  <div class="audit-page">
    <PageHero
      title="Auditoría Tributaria"
      subtitle="Vaciado F-200 por contribuyente y gestión"
      gradient="linear-gradient(135deg, #1e1b4b 0%, #4338ca 50%, #818cf8 100%)"
    >
      <div class="hero-badge" v-if="report">
        {{ report.taxpayer_name }}
      </div>
    </PageHero>

    <!-- Filters -->
    <div class="card filter-bar">
      <div class="filter-row">
        <div class="filter-group">
          <label class="form-label">Contribuyente</label>
          <select v-model="nit" :disabled="isFetchingTaxpayers" class="form-select">
            <option v-if="isFetchingTaxpayers" value="">Cargando...</option>
            <option v-for="t in taxpayers" :key="t.nit" :value="t.nit">
              {{ t.name }} (NIT: {{ t.nit }})
            </option>
          </select>
        </div>
        <div class="filter-group narrow">
          <label class="form-label">Gestión (Año)</label>
          <select v-model="year" class="form-select">
            <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="filter-action">
          <button class="btn btn-primary" @click="fetchReport" :disabled="isLoading || !nit">
            <svg v-if="!isLoading" xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <span v-else class="spin-small"></span>
            {{ isLoading ? 'Cargando...' : 'Generar' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="report" class="report-section">
      <!-- Action bar -->
      <div class="action-bar card">
        <div class="company-info">
          <h2>{{ report.taxpayer_name }}</h2>
          <span class="meta">NIT: {{ report.taxpayer_nit }} &nbsp;|&nbsp; Gestión: {{ report.year }}</span>
        </div>
        <div class="export-btns">
          <button class="btn btn-success" @click="downloadExcel">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>
            Excel
          </button>
          <button class="btn btn-danger" @click="downloadPdf">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            PDF
          </button>
        </div>
      </div>

      <!-- Audit Table -->
      <div class="table-card">
        <div class="table-scroll">
          <table class="audit-table">
            <thead>
              <tr class="header-row">
                <th class="sticky-col lbl-col">DETALLE</th>
                <th class="sticky-col cod-col">COD</th>
                <th v-for="m in months" :key="m" class="month-col">{{ m }}</th>
                <th class="total-col">TOTAL</th>
              </tr>
              <tr class="meta-row">
                <td class="sticky-col lbl-col side-label">Fecha presentación</td>
                <td class="sticky-col cod-col">-</td>
                <td v-for="(d, i) in report.presentation_dates" :key="i" class="center date-cell">{{ formatDate(d) }}</td>
                <td class="total-cell">-</td>
              </tr>
              <tr class="meta-row">
                <td class="sticky-col lbl-col side-label">Número de orden</td>
                <td class="sticky-col cod-col">-</td>
                <td v-for="(n, i) in report.transaction_numbers" :key="i" class="center order-cell">
                  {{ n ? (n.length > 8 ? '…' + n.slice(-8) : n) : '-' }}
                </td>
                <td class="total-cell">-</td>
              </tr>
            </thead>
            <tbody>
              <template v-for="group in getGroupedRows()" :key="group.name">
                <tr class="rubric-row">
                  <td colspan="15">{{ group.name }}</td>
                </tr>
                <tr v-for="row in group.rows" :key="row.field_code" class="data-row">
                  <td class="sticky-col lbl-col">{{ row.label }}</td>
                  <td class="sticky-col cod-col code-cell">{{ row.field_code }}</td>
                  <td v-for="(val, i) in row.months" :key="i" class="amount-cell" :class="{ zero: val == 0 }">
                    {{ formatCurrency(val) }}
                  </td>
                  <td class="total-cell">{{ formatCurrency(row.total) }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-page { max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem; }

.hero-badge {
  background: rgba(255,255,255,.15); color: white; font-weight: 700;
  font-size: 0.8rem; padding: 0.4rem 0.9rem; border-radius: 20px;
  border: 1px solid rgba(255,255,255,.25); position: relative; z-index: 1;
  max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Filter bar */
.filter-bar { margin-bottom: 0; }
.filter-row { display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap; }
.filter-group { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; min-width: 200px; }
.filter-group.narrow { max-width: 150px; }
.filter-action { flex-shrink: 0; }
@media (max-width: 600px) {
  .filter-group, .filter-group.narrow { min-width: 100%; max-width: 100%; }
  .filter-action { width: 100%; }
  .filter-action .btn { width: 100%; }
}

/* Action bar */
.action-bar {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0;
}
.company-info h2 { margin: 0 0 0.2rem; font-size: 1.1rem; font-weight: 700; }
.meta { font-size: 0.82rem; color: var(--text-muted); }
.export-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; }

/* Spinner inline */
.spin-small {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,.3); border-top-color: white;
  border-radius: 50%; animation: sp 0.8s linear infinite;
}
@keyframes sp { to { transform: rotate(360deg); } }

/* Table card */
.table-card {
  background: white; border-radius: 14px; border: 1px solid var(--border);
  box-shadow: var(--shadow-sm); overflow: hidden;
}
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }

.audit-table {
  border-collapse: collapse; font-size: 0.72rem; width: 100%;
}

.header-row th {
  background: linear-gradient(135deg, #1e1b4b, #3730a3);
  color: white; padding: 0.6rem 0.5rem; white-space: nowrap;
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.04em;
  text-transform: uppercase;
}

.total-col {
  background: linear-gradient(135deg, #312e81, #1e1b4b) !important;
  min-width: 110px;
}

.sticky-col { position: sticky; z-index: 2; background: inherit; }
.lbl-col { left: 0; width: 260px; min-width: 260px; max-width: 260px; }
.cod-col { left: 260px; width: 50px; text-align: center; }

.month-col { min-width: 88px; text-align: center; }

.meta-row td {
  background: linear-gradient(to right, #f0f4ff, #e8f0fe);
  padding: 0.4rem 0.5rem; font-weight: 600;
  text-align: center; font-size: 0.68rem; color: #3730a3;
}
.side-label { text-align: left !important; color: var(--text-muted) !important; }

.rubric-row td {
  background: linear-gradient(to right, #ede9fe, #ddd6fe);
  font-weight: 800; color: #3b0764;
  padding: 0.45rem 0.75rem; text-transform: uppercase;
  font-size: 0.68rem; letter-spacing: 0.04em;
}

.data-row td { padding: 0.5rem 0.5rem; border-bottom: 1px solid #f8fafc; vertical-align: middle; }
.data-row:hover td { background: #fafbff; }

.amount-cell { text-align: right; font-family: monospace; font-variant-numeric: tabular-nums; }
.amount-cell.zero { color: #cbd5e1; }
.date-cell { font-size: 0.65rem; }
.order-cell { font-size: 0.62rem; color: var(--primary); }
.code-cell { text-align: center; font-family: monospace; color: var(--text-muted); }

.total-cell {
  background: #f0f4ff; font-weight: 800; text-align: right;
  font-family: monospace; font-variant-numeric: tabular-nums;
  border-left: 2px solid #c7d2fe; color: #3730a3;
}
</style>
