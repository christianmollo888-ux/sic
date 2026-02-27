<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import PageHero from '../components/PageHero.vue'
import ExcelPreviewModal from '../components/ExcelPreviewModal.vue'

const taxpayers = ref<any[]>([])
const isFetchingTaxpayers = ref(true)

const nit = ref('')
const year = ref(new Date().getFullYear())
const availableYears = [2022, 2023, 2024, 2025, 2026]

// Modal state
const showPreview = ref(false)
const reportData = ref(null)
const isFetchingReport = ref(false)

const fetchTaxpayers = async () => {
  isFetchingTaxpayers.value = true
  try {
    const resp = await axios.get('http://localhost:8010/forms/taxpayers')
    taxpayers.value = resp.data
    if (taxpayers.value.length > 0) nit.value = taxpayers.value[0].nit
  } catch (e: any) { console.error("Error fetching taxpayers:", e) }
  finally { isFetchingTaxpayers.value = false }
}

const previewReport = async () => {
  if (!nit.value) return
  isFetchingReport.value = true
  try {
    const resp = await axios.get(`http://localhost:8010/forms/reports/tax-audit?nit=${nit.value}&year=${year.value}`)
    reportData.value = resp.data
    showPreview.value = true
  } catch (e: any) {
    console.error("Error fetching report data:", e)
    alert("Error al cargar los datos del reporte")
  } finally {
    isFetchingReport.value = false
  }
}

const downloadExcel = () => {
  if (!nit.value) return
  const url = `http://localhost:8010/forms/reports/resumen-200/excel?nit=${nit.value}&year=${year.value}`
  window.open(url)
}

onMounted(() => {
  fetchTaxpayers()
})
</script>

<template>
  <div class="resumen-page">
    <PageHero
      title="Resumen Formulario 200"
      subtitle="Generación de reporte consolidado anual en formato Excel SIAT"
      gradient="linear-gradient(135deg, #065f46 0%, #059669 50%, #34d399 100%)"
    />

    <div class="card selection-card">
      <div class="card-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="header-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        <h3>Parámetros del Reporte</h3>
      </div>
      
      <div class="card-body">
        <p class="instruction">Seleccione el contribuyente y la gestión para generar el archivo Excel consolidado o visualizar el resumen en pantalla.</p>
        
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Contribuyente</label>
            <select v-model="nit" :disabled="isFetchingTaxpayers" class="form-select">
              <option v-if="isFetchingTaxpayers" value="">Cargando...</option>
              <option v-for="t in taxpayers" :key="t.nit" :value="t.nit">
                {{ t.name }} (NIT: {{ t.nit }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Gestión (Año)</label>
            <select v-model="year" class="form-select">
              <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
        </div>

        <div class="actions-row">
          <button class="btn btn-primary" @click="previewReport" :disabled="!nit || isFetchingReport">
            <svg v-if="!isFetchingReport" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <span v-else class="spinner-small"></span>
            Ver Pantalla
          </button>
          
          <button class="btn btn-success" @click="downloadExcel" :disabled="!nit">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Descargar Excel (.xlsx)
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Preview -->
    <ExcelPreviewModal 
      :show="showPreview" 
      title="Resumen Formulario 200 - Vista Previa" 
      :reportData="reportData" 
      @close="showPreview = false" 
    />

    <div class="info-card card">
      <div class="info-content">
        <div class="info-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        </div>
        <div class="info-text">
          <h4>Sobre este reporte</h4>
          <p>Este reporte utiliza la plantilla oficial <code>ResumenFormulario200.xlsx</code> para consolidar las 12 declaraciones mensuales del año seleccionado. Asegúrese de haber procesado los PDFs de cada mes en la sección de "Procesar Formulario" para que la información esté completa.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.resumen-page {
  max-width: 900px;
  margin: 0 auto;
  display: flex; flex-direction: column; gap: 2rem;
}
.selection-card { padding: 0; overflow: hidden; }
.card-header {
  background: #f8fafc; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 0.75rem;
}
.header-icon { color: #059669; }
.card-header h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: var(--text); }
.card-body { padding: 2rem; }
.instruction { color: var(--text-muted); margin-bottom: 2rem; font-size: 0.95rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2.5rem; }
@media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }
.actions-row { display: flex; gap: 1rem; }
.actions-row .btn { flex: 1; padding: 1rem; font-weight: 700; border-radius: 12px; display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: all 0.2s; }
.actions-row .btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
@media (max-width: 600px) { .actions-row { flex-direction: column; } }

.spinner-small {
  width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.info-card { background: #ecfdf5; border: 1px solid #a7f3d0; }
.info-content { display: flex; gap: 1rem; padding: 1.25rem; }
.info-icon { color: #059669; flex-shrink: 0; }
.info-text h4 { margin: 0 0 0.5rem; color: #064e3b; font-size: 1rem; }
.info-text p { margin: 0; color: #065f46; font-size: 0.9rem; line-height: 1.5; }
code { background: rgba(255,255,255,0.5); padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace; }
</style>
