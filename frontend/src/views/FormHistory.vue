<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { useNotifications } from '../composables/useNotifications'

const { notify, confirm } = useNotifications()

const API_URL = 'http://localhost:8000'

interface DeclarationSummary {
  id: number
  taxpayer_name: string
  taxpayer_nit: string
  form_code: string
  version_number: string
  month: number
  year: number
  submission_date: string
  status: string
  transaction_number: string | null
}

const history = ref<DeclarationSummary[]>([])
const totalItems = ref(0)
const isLoading = ref(false)
const error = ref<string | null>(null)
const selectedDeclaration = ref<any>(null)
const isDetailsLoading = ref(false)
const showModal = ref(false)
const isDeleting = ref<number | null>(null)
const modalSearchTerm = ref('')

// Filters
const filters = ref({
  nit: '',
  formCode: '',
  year: '',
  month: ''
})

// Pagination
const pagination = ref({
  page: 1,
  limit: 10
})
const totalPages = computed(() => Math.ceil(totalItems.value / pagination.value.limit) || 1)

const fetchHistory = async () => {
  isLoading.value = true
  error.value = null
  try {
    const params: any = {
      skip: (pagination.value.page - 1) * pagination.value.limit,
      limit: pagination.value.limit
    }
    
    if (filters.value.nit && filters.value.nit.trim()) params.taxpayer_nit = filters.value.nit.trim()
    if (filters.value.formCode) params.form_code = filters.value.formCode
    
    const yearVal = parseInt(filters.value.year)
    if (!isNaN(yearVal)) params.year = yearVal
    
    const monthVal = parseInt(filters.value.month)
    if (!isNaN(monthVal)) params.month = monthVal

    console.log('Fetching history with params:', params)
    const response = await axios.get(`${API_URL}/forms/declarations`, { params })
    
    // Ensure we handle both structure: direct list or {items, total}
    if (response.data && response.data.items) {
      history.value = response.data.items
      totalItems.value = response.data.total
    } else if (Array.isArray(response.data)) {
      history.value = response.data
      totalItems.value = response.data.length
    } else {
      history.value = []
      totalItems.value = 0
    }
  } catch (err: any) {
    error.value = 'Error al cargar el historial. Verifique la conexión con el servidor.'
    console.error('Fetch history error:', err)
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => {
  pagination.value.page = 1
  fetchHistory()
}

const clearFilters = () => {
  filters.value = { nit: '', formCode: '', year: '', month: '' }
  applyFilters()
}

const prevPage = () => {
  if (pagination.value.page > 1) {
    pagination.value.page--
    fetchHistory()
  }
}

const nextPage = () => {
  if (pagination.value.page < totalPages.value) {
    pagination.value.page++
    fetchHistory()
  }
}

const fetchDetails = async (id: number) => {
  isDetailsLoading.value = true
  selectedDeclaration.value = null
  showModal.value = true
  try {
    const response = await axios.get(`${API_URL}/forms/declarations/${id}`)
    selectedDeclaration.value = response.data
  } catch (err: any) {
    console.error('Error al cargar detalles:', err)
    error.value = 'Error al cargar los detalles del formulario.'
    showModal.value = false
  } finally {
    isDetailsLoading.value = false
  }
}

const confirmDelete = async (id: number) => {
  const confirmed = await confirm({
    title: 'Eliminar Declaración',
    message: '¿Está seguro de que desea eliminar esta declaración? Esta acción no se puede deshacer y borrará todos los datos asociados.',
    confirmText: 'Sí, eliminar',
    cancelText: 'Cancelar',
    danger: true
  })

  if (!confirmed) return

  isDeleting.value = id
  try {
    await axios.delete(`${API_URL}/forms/declarations/${id}`)
    notify('Declaración eliminada correctamente', 'success')
    // Refresh history
    fetchHistory()
    if (selectedDeclaration.value && selectedDeclaration.value.header && selectedDeclaration.value.header.id === id) {
      selectedDeclaration.value = null
      showModal.value = false
    }
  } catch (err: any) {
    console.error('Error al eliminar:', err)
    notify('Error al eliminar la declaración. Intente nuevamente.', 'error')
  } finally {
    isDeleting.value = null
  }
}

const closeModal = () => {
  showModal.value = false
  modalSearchTerm.value = ''
  setTimeout(() => {
    selectedDeclaration.value = null
  }, 300)
}

const filteredModalValues = computed(() => {
  if (!selectedDeclaration.value || !selectedDeclaration.value.values) return []
  if (!modalSearchTerm.value.trim()) return selectedDeclaration.value.values
  
  const term = modalSearchTerm.value.toLowerCase().trim()
  return selectedDeclaration.value.values.filter((v: any) => 
    v.field_code.toLowerCase().includes(term) || 
    v.label.toLowerCase().includes(term) ||
    v.rubric.toLowerCase().includes(term)
  )
})

const groupedModalValues = computed(() => {
  const filtered = filteredModalValues.value
  if (!filtered.length) return []
  
  const groups: Record<string, any[]> = {}
  filtered.forEach((val: any) => {
    const rubric = val.rubric || 'General'
    if (!groups[rubric]) {
      groups[rubric] = []
    }
    groups[rubric].push(val)
  })
  
  return Object.entries(groups).map(([rubric, items]) => ({
    rubric,
    items
  })).sort((a, b) => a.rubric.localeCompare(b.rubric, undefined, { numeric: true, sensitivity: 'base' }))
})

// Watch to prevent body scroll when modal is open
watch(showModal, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('es-BO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('es-BO', { minimumFractionDigits: 2 }).format(value)
}

onMounted(fetchHistory)
</script>

<template>
  <div class="history-container">
    <header class="page-header">
      <div class="header-content">
        <h1>Historial de Formularios</h1>
        <p class="subtitle">Gestión, búsqueda y detalles de declaraciones procesadas</p>
      </div>
    </header>

    <!-- Filtros de Búsqueda -->
    <div class="filter-card card mb-4">
      <div class="filter-grid">
        <div class="filter-group">
          <label>NIT Contribuyente</label>
          <input type="text" v-model="filters.nit" placeholder="Ej. 1234567" class="form-input" @keyup.enter="applyFilters">
        </div>
        <div class="filter-group">
          <label>Formulario</label>
          <select v-model="filters.formCode" class="form-select" @change="applyFilters">
            <option value="">Todos</option>
            <option value="200">F-200 (IVA)</option>
            <option value="400">F-400 (IT)</option>
            <option value="605">F-605</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Gestión</label>
          <input type="number" v-model="filters.year" placeholder="Ej. 2025" class="form-input" @keyup.enter="applyFilters">
        </div>
        <div class="filter-group">
          <label>Periodo (Mes)</label>
          <select v-model="filters.month" class="form-select" @change="applyFilters">
            <option value="">Todos</option>
            <option v-for="m in 12" :key="m" :value="m">{{ m.toString().padStart(2, '0') }}</option>
          </select>
        </div>
        <div class="filter-actions">
          <button class="btn btn-primary" @click="applyFilters">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            Filtrar
          </button>
          <button class="btn btn-outline" @click="clearFilters">Limpiar</button>
        </div>
      </div>
    </div>

    <!-- Cargando general -->
    <div v-if="isLoading && (!history || history.length === 0)" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando historial...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Content Area -->
    <div v-else class="history-grid">
      <!-- Tabla -->
      <div class="table-card" :class="{ 'loading-opacity': isLoading }">
        <div class="table-responsive">
          <table class="history-table">
            <thead>
              <tr>
                <th>Contribuyente</th>
                <th>Formulario</th>
                <th>Periodo</th>
                <th>Fecha de Carga</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in history" :key="item.id" :class="{'active-row': selectedDeclaration && selectedDeclaration.header && selectedDeclaration.header.id === item.id}">
                <td data-label="Contribuyente">
                  <div class="taxpayer-info">
                    <span class="name">{{ item.taxpayer_name }}</span>
                    <span class="nit">NIT: {{ item.taxpayer_nit }}</span>
                  </div>
                </td>
                <td data-label="Formulario">
                  <div class="form-info">
                    <span class="form-badge">F-{{ item.form_code || '?' }}</span>
                    <span class="version">v.{{ item.version_number || '?' }}</span>
                  </div>
                </td>
                <td data-label="Periodo" class="period">{{ item.month.toString().padStart(2, '0') }}/{{ item.year }}</td>
                <td data-label="Fecha" class="date">{{ formatDate(item.submission_date) }}</td>
                <td data-label="Estado"><span class="status-badge">{{ item.status }}</span></td>
                <td data-label="Acciones">
                  <div class="action-buttons">
                    <button class="btn-icon btn-view" @click="fetchDetails(item.id)" title="Ver Detalles">
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    </button>
                    <button class="btn-icon btn-delete" @click="confirmDelete(item.id)" :disabled="isDeleting === item.id" title="Borrar">
                      <svg v-if="isDeleting !== item.id" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                      <div v-else class="spinner-small"></div>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!history || history.length === 0">
                <td colspan="6" class="empty-state">
                  <div class="empty-content">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="empty-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    <p>No se encontraron registros con los filtros actuales.</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Paginación Premium -->
        <div class="pagination-container" v-if="totalItems > 0">
          <div class="pagination-stats">
            Mostrando <strong>{{ (pagination.page - 1) * pagination.limit + 1 }}-{{ Math.min(pagination.page * pagination.limit, totalItems) }}</strong> de <strong>{{ totalItems }}</strong> registros
          </div>
          
          <div class="pagination-controls">
            <button class="p-btn p-btn-nav" :disabled="pagination.page === 1" @click="prevPage" title="Anterior">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            
            <div class="p-pages">
              <button 
                v-for="p in Math.min(5, totalPages)" 
                :key="p" 
                class="p-btn p-btn-page" 
                :class="{ 'p-active': pagination.page === p }"
                @click="pagination.page = p; fetchHistory()"
              >
                {{ p }}
              </button>
              <span v-if="totalPages > 5" class="p-dots">...</span>
              <button 
                v-if="totalPages > 5" 
                class="p-btn p-btn-page" 
                :class="{ 'p-active': pagination.page === totalPages }"
                @click="pagination.page = totalPages; fetchHistory()"
              >
                {{ totalPages }}
              </button>
            </div>

            <button class="p-btn p-btn-nav" :disabled="pagination.page >= totalPages" @click="nextPage" title="Siguiente">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Detalles -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div v-if="selectedDeclaration || isDetailsLoading" class="modal-content details-modal">
        <div v-if="isDetailsLoading" class="loading-state mini">
          <div class="spinner"></div>
          <span class="small-text">Cargando detalles...</span>
        </div>
        
        <div v-else-if="selectedDeclaration" class="details-content">
          <div class="details-header">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-title"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              F-{{ selectedDeclaration.header.form_code || '200' }} 
              <span class="badge-version">v.{{ selectedDeclaration.header.version_number || '6' }}</span>
            </h3>
            <button class="close-btn" @click="closeModal" title="Cerrar">&times;</button>
          </div>
          
          <div class="modal-body">
            <div class="header-info glossy-box">
              <div class="info-row"><label>Contribuyente:</label> <span class="highlight text-primary">{{ selectedDeclaration.header.business_name }}</span></div>
              <div class="info-row"><label>NIT:</label> <span>{{ selectedDeclaration.header.nit }}</span></div>
              <div class="divider"></div>
              <div class="info-row"><label>Periodo (Mes/Gestión):</label> <span class="period-text">{{ selectedDeclaration.header.month.toString().padStart(2, '0') }}/{{ selectedDeclaration.header.year }}</span></div>
              <div class="info-row"><label>Nº Orden/Transacción:</label> <span>{{ selectedDeclaration.header.transaction_number || '---' }}</span></div>
              <div class="info-row"><label>Fecha Presentación:</label> <span>{{ selectedDeclaration.header.presentation_date ? formatDate(selectedDeclaration.header.presentation_date) : '---' }}</span></div>
              <div class="info-row"><label>Usuario PDF:</label> <span class="small-text">{{ selectedDeclaration.header.pdf_user || '---' }}</span></div>
            </div>

            <div class="values-section">
              <div class="section-header">
                <h4 class="section-title">Valores Extraídos por Rubro / Casilla</h4>
                <div class="search-mini">
                  <input type="text" v-model="modalSearchTerm" placeholder="Buscar casilla o descripción..." class="mini-input">
                </div>
              </div>

              <div class="values-review-list">
                <div class="review-header">
                  <span class="col-code">Casilla</span>
                  <span class="col-desc">Descripción</span>
                  <span class="col-value">Monto (Bs.)</span>
                </div>
                
                <div v-for="group in groupedModalValues" :key="group.rubric" class="rubric-group">
                  <div class="rubric-group-header">
                    <span class="r-badge-large">{{ group.rubric }}</span>
                  </div>
                  <div v-for="val in group.items" :key="val.field_code" class="review-item">
                    <span class="col-code"><span class="c-badge">C-{{ val.field_code.replace('C','').replace('Casilla ','').trim() }}</span></span>
                    <span class="col-desc">{{ val.label }}</span>
                    <span class="col-value" :class="{ 'positive': val.value > 0 }">{{ formatCurrency(val.value) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-outline" @click="closeModal">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ─── Design Tokens ────────────────────────────────────────────────────── */
.history-container {
  --c-primary:       #2563eb;
  --c-primary-light: #3b82f6;
  --c-primary-glow:  rgba(37, 99, 235, 0.25);
  --c-surface:       #ffffff;
  --c-bg:            #f1f5f9;
  --c-text:          #0f172a;
  --c-muted:         #64748b;
  --c-border:        #e2e8f0;
  --c-danger:        #ef4444;
  --c-success:       #10b981;
  --radius-xl:       16px;
  --radius-lg:       12px;
  --radius-md:       8px;
  --radius-sm:       6px;
  --shadow-sm:       0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
  --shadow-md:       0 4px 16px rgba(0,0,0,.10), 0 2px 6px rgba(0,0,0,.06);
  --shadow-lg:       0 20px 40px rgba(0,0,0,.14), 0 8px 16px rgba(0,0,0,.08);

  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem;
  color: var(--c-text);
  background: var(--c-bg);
  min-height: 100vh;
}
@media (max-width: 768px) { .history-container { padding: 0.75rem; } }

/* ─── Page Hero Header ─────────────────────────────────────────────────── */
.page-header {
  background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 40%, #0ea5e9 100%);
  border-radius: var(--radius-xl);
  padding: 2.25rem 2.5rem;
  margin-bottom: 1.75rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(30, 58, 138, .4);
}

/* decorative circles */
.page-header::before,
.page-header::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
}
.page-header::before {
  width: 300px; height: 300px;
  background: white;
  top: -80px; right: -60px;
}
.page-header::after {
  width: 160px; height: 160px;
  background: white;
  bottom: -60px; right: 140px;
}

.header-content { position: relative; z-index: 1; }

.page-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.subtitle {
  color: rgba(255,255,255,.75);
  font-size: 0.95rem;
  margin: 0;
}

@media (max-width: 600px) {
  .page-header { padding: 1.5rem; }
  .page-header h1 { font-size: 1.4rem; }
}

/* ─── Filter Card ──────────────────────────────────────────────────────── */
.filter-card {
  background: var(--c-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--c-border);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
  min-width: 160px;
}

.filter-group label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--c-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.form-input,
.form-select {
  padding: 0.6rem 0.9rem;
  border: 1.5px solid var(--c-border);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  color: var(--c-text);
  background: #f8fafc;
  transition: all 0.2s;
  outline: none;
  width: 100%;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--c-primary);
  background: #ffffff;
  box-shadow: 0 0 0 3.5px var(--c-primary-glow);
}

.form-input:hover:not(:focus),
.form-select:hover:not(:focus) {
  border-color: #94a3b8;
}

.filter-actions {
  display: flex;
  gap: 0.6rem;
  flex: 0 0 auto;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .filter-actions { width: 100%; flex: 1 0 100%; }
  .filter-actions .btn { flex: 1; }
}

/* ─── Buttons ──────────────────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.875rem;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(.16,1,.3,1);
  cursor: pointer;
  border: 1.5px solid transparent;
  white-space: nowrap;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  border-color: #1d4ed8;
  box-shadow: 0 2px 8px rgba(37,99,235,.35);
}
.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37,99,235,.4);
}
.btn-primary:active { transform: translateY(0); }

.btn-outline {
  background: transparent;
  color: var(--c-muted);
  border-color: var(--c-border);
}
.btn-outline:hover {
  background: var(--c-bg);
  color: var(--c-text);
  border-color: #94a3b8;
}

/* ─── Table Card ───────────────────────────────────────────────────────── */
.table-card {
  background: var(--c-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--c-border);
  overflow: hidden;
  transition: opacity 0.3s;
}

.loading-opacity { opacity: 0.55; pointer-events: none; }

.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 620px;
}

.history-table thead tr {
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  border-bottom: 2px solid var(--c-border);
}

.history-table th {
  padding: 0.85rem 1.25rem;
  text-align: left;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--c-muted);
  letter-spacing: 0.07em;
  white-space: nowrap;
}

.history-table td {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.history-table tbody tr {
  transition: background 0.15s;
  background: var(--c-surface);
}

.history-table tbody tr:hover {
  background: #f8fbff;
}

.history-table tbody tr:last-child td { border-bottom: none; }

.history-table tbody tr.active-row {
  background: #eff6ff;
}
.history-table tbody tr.active-row td:first-child {
  border-left: 3px solid var(--c-primary);
}

/* ─── Cell Content ─────────────────────────────────────────────────────── */
.taxpayer-info { display: flex; flex-direction: column; gap: 0.15rem; }
.taxpayer-info .name {
  font-weight: 700;
  color: var(--c-text);
  font-size: 0.9rem;
  line-height: 1.3;
}
.taxpayer-info .nit {
  font-size: 0.75rem;
  color: var(--c-muted);
  font-family: 'Courier New', monospace;
  background: #f1f5f9;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  width: fit-content;
}

.form-info { display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-start; }
.form-badge {
  background: linear-gradient(135deg, #ede9fe, #ddd6fe);
  color: #5b21b6;
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  font-family: monospace;
  letter-spacing: 0.03em;
  border: 1px solid #c4b5fd;
}
.version { font-size: 0.68rem; color: var(--c-muted); padding-left: 0.25rem; }

.period {
  font-weight: 800;
  font-family: monospace;
  color: var(--c-text);
  font-size: 0.95rem;
  background: #f8fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--c-border);
  display: inline-block;
}

.date { font-size: 0.8rem; color: var(--c-muted); white-space: nowrap; }

.status-badge {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border: 1px solid #6ee7b7;
  display: inline-block;
  white-space: nowrap;
}

/* ─── Action Buttons ───────────────────────────────────────────────────── */
.action-buttons { display: flex; gap: 0.4rem; }

.btn-icon {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-muted);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(.16,1,.3,1);
  flex-shrink: 0;
}

.btn-view:hover {
  background: #eff6ff;
  color: var(--c-primary);
  border-color: #93c5fd;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59,130,246,.2);
}

.btn-delete:hover:not(:disabled) {
  background: #fff1f2;
  color: var(--c-danger);
  border-color: #fca5a5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239,68,68,.2);
}

.btn-icon:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

/* ─── Empty State ──────────────────────────────────────────────────────── */
.empty-state { padding: 3.5rem 1rem; text-align: center; }
.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.empty-icon {
  color: #cbd5e1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,.06));
}
.empty-content p {
  color: var(--c-muted);
  font-size: 0.95rem;
  margin: 0;
}

/* ─── Loading / Spinner ────────────────────────────────────────────────── */
.loading-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 1rem; padding: 4rem; color: var(--c-muted);
}
.loading-state.mini { padding: 3rem; }
.spinner {
  width: 44px; height: 44px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--c-primary);
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}
.loading-state.mini .spinner { width: 32px; height: 32px; }
@keyframes spin { to { transform: rotate(360deg); } }

.spinner-small {
  width: 15px; height: 15px;
  border: 2px solid #fecaca;
  border-top-color: var(--c-danger);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ─── Alerts ───────────────────────────────────────────────────────────── */
.alert {
  padding: 1rem 1.25rem; border-radius: var(--radius-lg);
  margin-bottom: 1.5rem; font-weight: 600;
  display: flex; align-items: center; gap: 0.75rem;
}
.alert-danger {
  background: #fef2f2; color: #b91c1c;
  border: 1px solid #fecaca;
}

/* ─── Pagination ───────────────────────────────────────────────────────── */
.pagination-container {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  border-top: 1px solid #f1f5f9;
  background: linear-gradient(to right, #fafafa, #f8fafc);
}

.pagination-stats {
  font-size: 0.82rem;
  color: var(--c-muted);
}
.pagination-stats strong { color: var(--c-text); }

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: center;
}

.p-pages {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.p-btn {
  display: flex; align-items: center; justify-content: center;
  background: var(--c-surface);
  border: 1.5px solid var(--c-border);
  color: var(--c-text);
  font-weight: 600;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: var(--radius-md);
}
.p-btn-nav { width: 34px; height: 34px; color: var(--c-muted); }
.p-btn-page { min-width: 34px; height: 34px; padding: 0 0.5rem; }
.p-btn:hover:not(:disabled) {
  border-color: var(--c-primary);
  color: var(--c-primary);
  background: #eff6ff;
  transform: translateY(-1px);
}
.p-btn:disabled { opacity: 0.35; cursor: not-allowed; background: #f8fafc; }
.p-active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  color: #fff !important;
  border-color: #1d4ed8 !important;
  box-shadow: 0 3px 10px rgba(37,99,235,.35);
}
.p-dots { color: var(--c-muted); padding: 0 0.35rem; }

@media (max-width: 600px) {
  .pagination-container { padding: 1rem; justify-content: center; }
}

/* ─── Modal ────────────────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(15,23,42,.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
  overflow-y: auto;
}

.details-modal {
  width: 95%;
  max-width: 1020px;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  background: var(--c-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  animation: modalIn 0.28s cubic-bezier(.16,1,.3,1);
  border: 1px solid rgba(255,255,255,.15);
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(24px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.details-header {
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid var(--c-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  flex-shrink: 0;
}

.details-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--c-text);
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.icon-title { color: var(--c-primary); }

.badge-version {
  font-size: 0.75rem;
  background: #e2e8f0;
  color: #475569;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
  font-weight: 700;
}

.close-btn {
  width: 36px; height: 36px;
  background: none; border: none;
  font-size: 1.6rem; line-height: 1;
  cursor: pointer;
  color: var(--c-muted);
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.close-btn:hover { color: var(--c-danger); background: #fff1f2; }

.modal-body {
  flex: 1; min-height: 0;
  overflow-y: auto;
}

.modal-body::-webkit-scrollbar { width: 6px; }
.modal-body::-webkit-scrollbar-track { background: #f8fafc; }
.modal-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.modal-body::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

.modal-footer {
  padding: 1rem 1.75rem;
  border-top: 1px solid var(--c-border);
  display: flex;
  justify-content: flex-end;
  background: #f8fafc;
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  flex-shrink: 0;
}

/* ─── Modal Body Content ───────────────────────────────────────────────── */
.header-info {
  margin: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
  border-radius: var(--radius-lg);
  border: 1px solid #dbeafe;
  box-shadow: inset 0 1px 4px rgba(37,99,235,.06);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.9rem;
  padding-bottom: 0.65rem;
  margin-bottom: 0.65rem;
  border-bottom: 1px solid rgba(226,232,240,.6);
}
.info-row:last-child { padding-bottom: 0; margin-bottom: 0; border-bottom: none; }
.info-row label {
  color: var(--c-muted); font-weight: 600;
  font-size: 0.78rem; text-transform: uppercase;
  letter-spacing: 0.04em;
}
.info-row span { font-weight: 700; color: var(--c-text); text-align: right; max-width: 60%; }

.text-primary { color: var(--c-primary) !important; }
.highlight { font-size: 1.05rem; }
.period-text {
  font-family: monospace; font-size: 1rem;
  background: white; padding: 0.15rem 0.5rem;
  border-radius: 5px; border: 1px solid var(--c-border);
}
.small-text { font-size: 0.78rem; color: var(--c-muted); }
.divider { height: 1px; background: var(--c-border); margin: 0.5rem 0; }

/* ─── Values Section ───────────────────────────────────────────────────── */
.values-section { padding: 0 1.5rem 2rem; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.section-title {
  font-size: 0.78rem;
  text-transform: uppercase;
  color: var(--c-muted);
  font-weight: 800;
  letter-spacing: 0.08em;
  margin: 0;
}

.search-mini { flex: 0 0 240px; }
@media (max-width: 600px) { .search-mini { flex: 1 0 100%; } }

.mini-input {
  width: 100%;
  padding: 0.5rem 0.8rem;
  border: 1.5px solid var(--c-border);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
  background: #f8fafc;
}
.mini-input:focus {
  border-color: var(--c-primary);
  background: white;
  box-shadow: 0 0 0 3px var(--c-primary-glow);
}

.values-review-list {
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: white;
  box-shadow: var(--shadow-sm);
}

.review-header {
  display: grid;
  grid-template-columns: 110px 1fr 150px;
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  padding: 0.65rem 1.25rem;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--c-muted);
  letter-spacing: 0.07em;
  border-bottom: 1px solid var(--c-border);
}

.rubric-group-header {
  background: linear-gradient(to right, #f0f9ff, #e0f2fe);
  padding: 0.55rem 1.25rem;
  border-bottom: 1px solid #bae6fd;
  display: flex;
  align-items: center;
}

.r-badge-large {
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #0369a1;
  background: linear-gradient(135deg, #bae6fd, #7dd3fc);
  padding: 0.3rem 0.7rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
  border: 1px solid #7dd3fc;
}

.review-item {
  display: grid;
  grid-template-columns: 110px 1fr 150px;
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  border-bottom: 1px solid #f8fafc;
  align-items: center;
  transition: background 0.15s;
}
.review-item:last-child { border-bottom: none; }
.review-item:hover { background: #fafbff; }

.col-code .c-badge {
  font-family: 'Courier New', monospace;
  font-weight: 700;
  background: #f1f5f9;
  color: #475569;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  border: 1px solid var(--c-border);
}

.col-desc { color: var(--c-text); font-weight: 500; line-height: 1.5; padding: 0 0.75rem; }
.col-value { font-weight: 800; text-align: right; font-size: 0.95rem; color: #64748b; font-variant-numeric: tabular-nums; }
.col-value.positive { color: var(--c-primary); }

/* ─── Responsive modal ─────────────────────────────────────────────────── */
@media (max-width: 800px) {
  .review-header { display: none; }
  .review-item { grid-template-columns: auto 1fr; gap: 0.4rem; }
  .col-desc { grid-column: 1 / -1; order: -1; padding: 0; font-weight: 600; }
  .col-value { grid-column: 1 / -1; text-align: left; border-top: 1px dashed #f1f5f9; padding-top: 0.4rem; }
}

@media (max-width: 640px) {
  .details-modal {
    max-height: 100vh; max-height: 100dvh;
    border-radius: 0; margin: 0; width: 100%;
  }
  .modal-backdrop { padding: 0; align-items: flex-end; }
  .details-header h3 { font-size: 1.05rem; }
  .details-header { padding: 1rem 1.25rem; }
  .header-info { margin: 0.75rem; padding: 1rem; }
  .values-section { padding: 0 0.75rem 1.5rem; }
}

/* ─── Mobile Table → Card Stack ────────────────────────────────────────── */
@media (max-width: 640px) {
  /* Hide table header on mobile */
  .history-table thead {
    display: none;
  }

  /* Make the table itself behave as a block */
  .history-table,
  .history-table tbody,
  .history-table tr {
    display: block;
    width: 100%;
  }

  /* Each row becomes a card */
  .history-table tbody tr {
    margin: 0.75rem;
    width: calc(100% - 1.5rem);
    border-radius: var(--radius-lg);
    border: 1.5px solid var(--c-border);
    box-shadow: var(--shadow-sm);
    background: var(--c-surface);
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
  }

  .history-table tbody tr:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }

  .history-table tbody tr.active-row {
    border-color: var(--c-primary);
    background: #eff6ff;
  }

  /* Each cell becomes a labeled row inside the card */
  .history-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    border-left: none;
    font-size: 0.875rem;
  }

  .history-table td:last-child {
    border-bottom: none;
  }

  /* Add the label on the left from data-label */
  .history-table td::before {
    content: attr(data-label);
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--c-muted);
    flex-shrink: 0;
    margin-right: 0.75rem;
    min-width: 80px;
  }

  /* Card header: Contribuyente row gets special styling */
  .history-table td[data-label="Contribuyente"] {
    background: linear-gradient(to right, #f8fafc, #eff6ff);
    padding: 0.85rem 1rem;
    border-bottom: 2px solid #dbeafe;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
  }

  .history-table td[data-label="Contribuyente"]::before {
    color: var(--c-primary);
    font-size: 0.6rem;
  }

  /* Actions row: full width buttons */
  .history-table td[data-label="Acciones"] {
    background: #fafbff;
    padding: 0.75rem 1rem;
  }

  .history-table td[data-label="Acciones"] .action-buttons {
    display: flex;
    gap: 0.5rem;
    width: 100%;
    justify-content: flex-end;
  }

  .history-table td[data-label="Acciones"] .btn-icon {
    width: 38px;
    height: 38px;
  }

  /* Status badge aligns right */
  .history-table td[data-label="Estado"] {
    justify-content: space-between;
  }

  /* Period cell */
  .history-table td.period {
    font-size: 1rem;
  }

  /* Remove min-width — table is now block */
  .history-table {
    min-width: unset;
  }

  /* Remove the outer scroll wrapper since it's no longer needed */
  .table-responsive {
    overflow-x: unset;
  }

  /* Filter grid stacks fully on mobile */
  .filter-group {
    min-width: 100%;
    flex: 1 0 100%;
  }
}

/* Medium screens — 2-col filter */
@media (max-width: 768px) and (min-width: 641px) {
  .filter-group {
    min-width: calc(50% - 0.5rem);
  }
}
</style>
