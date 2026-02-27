<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import PageHero from '../components/PageHero.vue'

const API_URL = 'http://localhost:8000'
const file = ref<File | null>(null)
const isDragging = ref(false)
const isLoading = ref(false)
const extractedData = ref<any>(null)
const error = ref<string | null>(null)
const isSaving = ref(false)
const saveSuccess = ref(false)

const onDragOver = (e: DragEvent) => { e.preventDefault(); isDragging.value = true }
const onDragLeave = () => { isDragging.value = false }
const onDrop = (e: DragEvent) => {
  e.preventDefault(); isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    if (files[0].type === 'application/pdf') { file.value = files[0]; error.value = null }
    else error.value = 'Por favor, sube un archivo PDF válido.'
  }
}
const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) { file.value = target.files[0]; error.value = null }
}

const processFile = async () => {
  if (!file.value) return
  isLoading.value = true; error.value = null; extractedData.value = null; saveSuccess.value = false
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const response = await axios.post(`${API_URL}/forms/process-pdf`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    extractedData.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al procesar el archivo.'
  } finally { isLoading.value = false }
}

const saveDeclaration = async () => {
  if (!extractedData.value) return
  isSaving.value = true; error.value = null
  const parsePdfDate = (str: string | null) => {
    if (!str) return null
    const parts = str.match(/(\d+)\/(\d+)\/(\d+)\s+([\d:]+)/)
    if (parts) { const [_, d, m, y, time] = parts; return `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}T${time}` }
    return str
  }
  const payload = {
    taxpayer_nit: extractedData.value.header.nit,
    taxpayer_name: extractedData.value.header.business_name,
    form_code: "200", version_number: extractedData.value.header.version || "6",
    month: parseInt(extractedData.value.header.month), year: parseInt(extractedData.value.header.year),
    presentation_date: parsePdfDate(extractedData.value.header.presentation_date),
    print_date: parsePdfDate(extractedData.value.header.print_date),
    pdf_user: extractedData.value.header.pdf_user, values: [] as any[]
  }
  const allRubros = [extractedData.value.rubro1, extractedData.value.rubro2, extractedData.value.rubro3]
  allRubros.forEach(rubro => { for (const [key, value] of Object.entries(rubro)) payload.values.push({ field_code: key, value }) })
  try {
    await axios.post(`${API_URL}/forms/declarations`, payload)
    saveSuccess.value = true; extractedData.value = null; file.value = null
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al guardar la declaración.'
  } finally { isSaving.value = false }
}

const formatCurrency = (value: number) => new Intl.NumberFormat('es-BO', { minimumFractionDigits: 2 }).format(value)
const getCasillaLabel = (code: string) => {
  const labels: Record<string, string> = {
    'C13': 'Ventas de bienes/servicios gravados', 'C1002': 'Total Débito Fiscal',
    'C11': 'Total Compras', 'C1004': 'Total Crédito Fiscal',
    'C693': 'Diferencia a favor del Contribuyente', 'C909': 'Impuesto Determinado a favor del Fisco'
  }
  return labels[code] || `Casilla ${code.substring(1)}`
}
</script>

<template>
  <div class="upload-page">
    <PageHero
      title="Carga de Formulario PDF"
      subtitle="Formulario 200 (IVA) — Versión 6 · Extracción automatizada de datos"
      gradient="linear-gradient(135deg, #701a75 0%, #a21caf 45%, #e879f9 100%)"
    />

    <!-- Upload Zone -->
    <div class="drop-zone" :class="{ dragging: isDragging, 'has-file': !!file }"
         @dragover="onDragOver" @dragleave="onDragLeave" @drop="onDrop">

      <div v-if="!file" class="drop-inner">
        <div class="upload-icon-wrap">
          <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
        <h3>Arrastra tu archivo PDF aquí</h3>
        <p>o haz clic en el área para seleccionar</p>
        <span class="format-note">Solo archivos PDF · Formulario F-200</span>
      </div>
      <input v-if="!file" type="file" @change="onFileChange" accept="application/pdf" class="file-input" />

      <div v-else class="file-selected">
        <div class="file-icon-wrap">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div class="file-details">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
        </div>
        <button class="btn btn-outline btn-sm" @click="file = null; saveSuccess = false" :disabled="isLoading">Cambiar</button>
      </div>

      <div v-if="file && !extractedData" class="upload-action">
        <button class="btn btn-primary btn-lg" @click="processFile" :disabled="isLoading">
          <span v-if="isLoading" class="spin-w"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          {{ isLoading ? 'Procesando...' : 'Procesar Formulario' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="saveSuccess" class="alert alert-success">✅ ¡Formulario guardado con éxito en el historial!</div>

    <!-- Extracted Results -->
    <div v-if="extractedData" class="results">
      <!-- Header info card -->
      <div class="card results-header">
        <div class="results-title-bar">
          <div>
            <h3>Datos Extraídos</h3>
            <p class="text-muted" style="margin:0;font-size:.85rem">Revisa la información antes de guardar</p>
          </div>
          <button class="btn btn-primary" @click="saveDeclaration" :disabled="isSaving">
            <span v-if="isSaving" class="spin-w"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            {{ isSaving ? 'Guardando...' : 'Guardar en Historial' }}
          </button>
        </div>
        <div class="header-grid">
          <div class="info-chip">
            <span class="chip-label">NIT</span>
            <span class="chip-val">{{ extractedData.header.nit || '---' }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">Período</span>
            <span class="chip-val">{{ extractedData.header.month }}/{{ extractedData.header.year }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">Versión</span>
            <span class="chip-val">v{{ extractedData.header.version }}</span>
          </div>
          <div class="info-chip full">
            <span class="chip-label">Razón Social</span>
            <span class="chip-val">{{ extractedData.header.business_name || '---' }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">Presentación</span>
            <span class="chip-val mono">{{ extractedData.header.presentation_date || '---' }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">Impresión</span>
            <span class="chip-val mono">{{ extractedData.header.print_date || '---' }}</span>
          </div>
          <div class="info-chip">
            <span class="chip-label">Usuario PDF</span>
            <span class="chip-val mono">{{ extractedData.header.pdf_user || '---' }}</span>
          </div>
        </div>
      </div>

      <!-- Rubros grid -->
      <div class="rubros-grid">
        <div v-for="(fields, rubroKey) in { 'Rubro 1: Débito Fiscal': extractedData.rubro1, 'Rubro 2: Crédito Fiscal': extractedData.rubro2, 'Rubro 3: Diferencia': extractedData.rubro3 }"
             :key="rubroKey" class="card rubro-card">
          <div class="rubro-header">
            <span class="rubro-badge">{{ String(rubroKey).split(':')[0] }}</span>
            <span class="rubro-name">{{ String(rubroKey).split(':')[1]?.trim() }}</span>
          </div>
          <div class="field-list">
            <div v-for="(value, key) in fields" :key="key" class="field-row">
              <div class="field-left">
                <span class="field-code">{{ String(key).substring(1) }}</span>
                <span class="field-desc">{{ getCasillaLabel(String(key)) }}</span>
              </div>
              <span class="field-val" :class="{ positive: (value as number) > 0 }">
                {{ formatCurrency(value as number) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-page { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem; }

/* ─ Drop zone ─────────────────────────────────────────────────── */
.drop-zone {
  border: 2px dashed var(--border);
  border-radius: 16px;
  background: white;
  padding: 2.5rem;
  text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 1.25rem;
  position: relative;
  transition: all 0.3s;
  box-shadow: var(--shadow-sm);
}
.drop-zone.dragging {
  border-color: var(--primary);
  background: #eff6ff;
  box-shadow: 0 0 0 4px rgba(37,99,235,.12);
}
.drop-zone.has-file { border-style: solid; border-color: #93c5fd; }

.file-input {
  position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
}

.drop-inner h3 { margin: 0 0 0.35rem; font-size: 1.15rem; font-weight: 700; }
.drop-inner p { margin: 0 0 0.5rem; color: var(--text-muted); font-size: 0.9rem; }
.format-note { font-size: 0.75rem; color: var(--text-muted); background: #f1f5f9; padding: 0.25rem 0.6rem; border-radius: 20px; }

.upload-icon-wrap {
  width: 72px; height: 72px; background: linear-gradient(135deg, #f3e8ff, #fae8ff);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: #a21caf; margin: 0 auto;
  box-shadow: 0 4px 12px rgba(162,28,175,.2);
}

.file-selected {
  display: flex; align-items: center; gap: 1rem;
  background: #f8fafc; padding: 1rem 1.25rem; border-radius: 10px;
  border: 1px solid var(--border); width: 100%; max-width: 480px;
}
.file-icon-wrap { color: #a21caf; flex-shrink: 0; }
.file-details { flex: 1; text-align: left; display: flex; flex-direction: column; gap: 0.15rem; }
.file-name { font-weight: 700; font-size: 0.9rem; word-break: break-all; }
.file-size { font-size: 0.78rem; color: var(--text-muted); }

.btn-sm { padding: 0.4rem 0.8rem; font-size: 0.8rem; }
.btn-lg { padding: 0.75rem 2rem; font-size: 1rem; }

.spin-w {
  display: inline-block; width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,.3); border-top-color: white;
  border-radius: 50%; animation: sp 0.8s linear infinite;
}
@keyframes sp { to { transform: rotate(360deg); } }

/* ─ Results ───────────────────────────────────────────────────── */
.results { display: flex; flex-direction: column; gap: 1.5rem; animation: slideUp .4s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.results-header { position: relative; }
.results-title-bar { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.5rem; }
.results-title-bar h3 { margin: 0 0 0.2rem; font-size: 1.1rem; }

.header-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}
@media (max-width: 600px) { .header-grid { grid-template-columns: 1fr 1fr; } }

.info-chip { background: #f8fafc; border-radius: 10px; padding: 0.75rem; border: 1px solid var(--border); display: flex; flex-direction: column; gap: 0.2rem; }
.info-chip.full { grid-column: span 3; }
@media (max-width: 600px) { .info-chip.full { grid-column: span 2; } }
.chip-label { font-size: 0.62rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); letter-spacing: 0.06em; }
.chip-val { font-weight: 700; font-size: 1rem; color: var(--text); }
.chip-val.mono { font-family: monospace; font-size: 0.8rem; color: var(--primary); }

.rubros-grid { display: grid; grid-template-columns: 1fr; gap: 1.25rem; }
@media (min-width: 768px) { .rubros-grid { grid-template-columns: repeat(2, 1fr); } }

.rubro-card { padding: 0; overflow: hidden; }
.rubro-header {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.85rem 1.25rem; background: linear-gradient(to right, #f8fafc, #f3e8ff);
  border-bottom: 1px solid #e9d5ff;
}
.rubro-badge {
  background: linear-gradient(135deg, #a855f7, #7c3aed);
  color: white; padding: 0.2rem 0.6rem; border-radius: 20px;
  font-size: 0.68rem; font-weight: 800;
}
.rubro-name { font-weight: 700; font-size: 0.9rem; color: var(--text); }

.field-list { display: flex; flex-direction: column; padding: 0.5rem 0; }
.field-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.55rem 1.25rem; border-bottom: 1px solid #f8fafc;
  transition: background 0.15s;
}
.field-row:last-child { border-bottom: none; }
.field-row:hover { background: #fafbff; }
.field-left { display: flex; align-items: center; gap: 0.6rem; flex: 1; }
.field-code {
  background: #f1f5f9; font-family: monospace; font-weight: 700;
  font-size: 0.72rem; color: var(--text-muted);
  padding: 0.15rem 0.4rem; border-radius: 4px; flex-shrink: 0;
  border: 1px solid var(--border);
}
.field-desc { font-size: 0.82rem; color: var(--text); line-height: 1.3; }
.field-val { font-family: monospace; font-weight: 700; font-size: 0.9rem; color: #64748b; font-variant-numeric: tabular-nums; }
.field-val.positive { color: var(--primary); }
</style>
