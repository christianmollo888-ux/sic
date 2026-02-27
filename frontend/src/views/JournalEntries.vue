<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { entryService } from '../services/api'
import { useNotifications } from '../composables/useNotifications'
import PageHero from '../components/PageHero.vue'

const { notify } = useNotifications()

const entries = ref<any[]>([])
const loading = ref(true)
const totalRecords = ref(0)
const currentPage = ref(1)
const pageSize = 50

async function fetchEntries() {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize
    const res = await entryService.getAll(skip, pageSize)
    entries.value = res.data.items || res.data
    totalRecords.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const totalPages = computed(() => Math.max(1, Math.ceil(totalRecords.value / pageSize)))

function prevPage() {
  if (currentPage.value > 1) { currentPage.value--; fetchEntries() }
}
function nextPage() {
  if (currentPage.value < totalPages.value) { currentPage.value++; fetchEntries() }
}

onMounted(() => { fetchEntries() })

const showModal = ref(false)
const pdfUrl = ref('')
const currentPdfId = ref<number | null>(null)

function closePdfModal() {
  showModal.value = false
  if (pdfUrl.value) { window.URL.revokeObjectURL(pdfUrl.value); pdfUrl.value = '' }
  currentPdfId.value = null
}

function formatCurrency(val: number | string) {
  return new Intl.NumberFormat('es-BO', { style: 'currency', currency: 'BOB' }).format(Number(val))
}

const downloadingIds = ref<Set<number>>(new Set())

async function downloadComprobante(id: number) {
  if (downloadingIds.value.has(id)) return
  downloadingIds.value.add(id)
  try {
    const res = await entryService.getComprobantePdf(id)
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    pdfUrl.value = url
    currentPdfId.value = id
    showModal.value = true
  } catch (e) {
    console.error("Error downloading pdf", e)
    notify("Hubo un error al generar el comprobante PDF.", "error")
  } finally {
    downloadingIds.value.delete(id)
  }
}
</script>

<template>
  <div class="je-container">
    <PageHero
      title="Asientos Contables"
      subtitle="Registro histórico de transacciones diarias"
    >
      <div v-if="totalRecords > 0" class="hero-badge">
        {{ totalRecords.toLocaleString() }} registros
      </div>
    </PageHero>

    <div v-if="loading" class="loading-block">
      <div class="spinner-global"></div>
      <span>Cargando asientos...</span>
    </div>

    <div v-else>
      <div v-for="entry in entries" :key="entry.id" class="entry-card">
        <div class="entry-header">
          <div class="entry-meta">
            <span class="entry-type-badge">{{ entry.entry_type }}</span>
            <span class="entry-date">{{ entry.date }}</span>
            <span class="entry-num">#{{ entry.entry_number || entry.id }}</span>
          </div>
          <button class="btn btn-secondary btn-print" @click="downloadComprobante(entry.id)" :disabled="downloadingIds.has(entry.id)">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
            {{ downloadingIds.has(entry.id) ? 'Generando...' : 'Comprobante' }}
          </button>
        </div>
        <p class="entry-desc">{{ entry.description }}</p>

        <div class="detail-wrap">
          <table class="detail-table">
            <thead>
              <tr>
                <th>Cuenta</th>
                <th class="text-right">Debe</th>
                <th class="text-right">Haber</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="detail in entry.details" :key="detail.id">
                <td data-label="Cuenta">ID Cuenta: {{ detail.account_id }}</td>
                <td data-label="Debe" class="text-right amount">{{ formatCurrency(detail.debit) }}</td>
                <td data-label="Haber" class="text-right amount">{{ formatCurrency(detail.credit) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="totalPages > 1 && !loading">
      <button :disabled="currentPage === 1" @click="prevPage" class="btn btn-outline">
        ← Anterior
      </button>
      <span class="page-info">Página <strong>{{ currentPage }}</strong> de <strong>{{ totalPages }}</strong></span>
      <button :disabled="currentPage === totalPages" @click="nextPage" class="btn btn-outline">
        Siguiente →
      </button>
    </div>

    <!-- PDF Viewer Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closePdfModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Comprobante #{{ currentPdfId }}</h3>
          <button class="btn-close" @click="closePdfModal">&times;</button>
        </div>
        <div class="modal-body">
          <iframe :src="pdfUrl" class="pdf-frame" title="Previsualización Comprobante"></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.je-container { max-width: 1200px; margin: 0 auto; }

/* Hero badge */
.hero-badge {
  background: rgba(255,255,255,.15);
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 0.4rem 0.9rem;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,.25);
  backdrop-filter: blur(4px);
  position: relative;
  z-index: 1;
}

/* Entry Cards */
.entry-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
  border-left: 4px solid var(--primary);
  transition: box-shadow 0.2s, transform 0.2s;
}
.entry-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.10); transform: translateY(-1px); }

.entry-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.5rem;
}

.entry-meta { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }

.entry-type-badge {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af; padding: 0.2rem 0.6rem; border-radius: 20px;
  font-size: 0.72rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.04em; border: 1px solid #93c5fd;
}
.entry-date { font-weight: 600; font-size: 0.875rem; color: var(--text); }
.entry-num { color: var(--text-muted); font-size: 0.8rem; font-family: monospace; }

.btn-print { font-size: 0.8rem; padding: 0.4rem 0.9rem; }

.entry-desc {
  margin: 0 0 1rem;
  font-size: 0.9rem; line-height: 1.5;
  color: var(--text-muted); font-style: italic;
}

/* Detail Table */
.detail-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid #f1f5f9; }
.detail-table { width: 100%; border-collapse: collapse; min-width: 320px; font-size: 0.85rem; }
.detail-table th { background: #f8fafc; padding: 0.6rem 0.75rem; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; }
.detail-table td { padding: 0.65rem 0.75rem; border-bottom: 1px solid #f8fafc; color: var(--text); }
.detail-table tr:last-child td { border-bottom: none; }
.detail-table tbody tr:hover { background: #fafbff; }
.text-right { text-align: right; }
.amount { font-variant-numeric: tabular-nums; font-weight: 500; }

/* Pagination */
.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: 1rem; margin-top: 2rem; padding: 1rem 0; flex-wrap: wrap;
}
.page-info { font-size: 0.875rem; color: var(--text-muted); }

/* PDF Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.6);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000; padding: 1rem;
}
.modal-content {
  background: white; border-radius: 12px; width: 100%;
  max-width: 900px; height: 90vh; max-height: 88vh;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,.2);
}
.modal-header {
  padding: 1rem 1.5rem;
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  border-bottom: 1px solid var(--border);
}
.modal-header h3 { margin: 0; font-size: 1.1rem; }
.btn-close {
  background: none; border: none; font-size: 1.5rem; cursor: pointer;
  color: var(--text-muted); width: 32px; height: 32px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.btn-close:hover { background: #fee2e2; color: var(--danger); }
.modal-body { flex: 1; min-height: 0; }
.pdf-frame { width: 100%; height: 100%; border: none; }

/* Mobile: table rows → stacked */
@media (max-width: 540px) {
  .entry-card { padding: 1rem; }
  .detail-table thead { display: none; }
  .detail-table, .detail-table tbody, .detail-table tr { display: block; width: 100%; }
  .detail-table tr { padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9; }
  .detail-table tr:last-child { border-bottom: none; }
  .detail-table td {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.3rem 0.75rem;
  }
  .detail-table td::before {
    content: attr(data-label);
    font-size: 0.65rem; font-weight: 800;
    text-transform: uppercase; color: var(--text-muted);
    margin-right: 0.5rem;
  }
  .detail-table td.text-right { text-align: left; }
}
</style>
