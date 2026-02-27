<script setup lang="ts">
import { ref, computed } from 'vue'
import PageHero from '../components/PageHero.vue'

const endDate = ref('2025-12-31')
const startDateDiario = ref('2025-01-01')
const endDateDiario = ref('2025-12-31')
const bgStartDate = ref('2025-01-01')
const bgEndDate = ref('2025-12-31')
const loading = ref(false)
const error = ref('')
const reportData = ref<any[]>([])
const erReportData = ref<any>(null)
const diarioReportData = ref<any[] | null>(null)
const bgReportData = ref<any | null>(null)
const reportType = ref<'BSS' | 'ER' | 'DIARIO' | 'DIARIO_EXCEL' | 'BG' | ''>('')

const getVoucherTypeName = (typeCode: string | number) => {
  const mapping: Record<string, string> = {
    '1': 'INGRESO',
    '2': 'EGRESO',
    '3': 'DIARIO',
    '11': 'AJUSTE',
  };
  return mapping[String(typeCode)] || 'CONTABLE';
}

const totalBSS = computed(() => {
  if (!reportData.value.length) return { debit: 0, credit: 0, deudor: 0, acreedor: 0 };
  const L5 = reportData.value.filter((r: any) => r.level === 5);
  return {
    debit: L5.reduce((sum, r) => sum + Number(r.debit), 0),
    credit: L5.reduce((sum, r) => sum + Number(r.credit), 0),
    deudor: L5.reduce((sum, r) => sum + Number(r.deudor), 0),
    acreedor: L5.reduce((sum, r) => sum + Number(r.acreedor), 0),
  };
})

const generateBSS = async (preview = false) => {
  loading.value = true
  error.value = ''
  reportData.value = []
  erReportData.value = null
  reportType.value = 'BSS'
  
  try {
    // Determine API URL based on environment or window location
    const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
    
    if (preview) {
        const response = await fetch(`${apiUrl}/reports/bss?end_date=${endDate.value}&format=json`)
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Error al generar el reporte');
        }
        const data = await response.json()
        reportData.value = data.data
    } else {
        const response = await fetch(`${apiUrl}/reports/bss?end_date=${endDate.value}`)
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Error al generar el reporte');
        }
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        
        const a = document.createElement('a')
        a.href = url
        a.download = `BSS_SIC4BUS_${endDate.value}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const generateER = async () => {
  loading.value = true
  error.value = ''
  reportData.value = []
  erReportData.value = null
  reportType.value = 'ER'
  
  try {
    const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
    const response = await fetch(`${apiUrl}/reports/er?end_date=${endDate.value}`)
    
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Error al generar el reporte');
    }
    const data = await response.json()
    erReportData.value = data.data
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const generateDiario = async (preview = false) => {
  loading.value = true
  error.value = ''
  reportData.value = []
  erReportData.value = null
  diarioReportData.value = null
  reportType.value = 'DIARIO'
  
  try {
    const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
    
    if (preview) {
      const response = await fetch(`${apiUrl}/reports/diario?start_date=${startDateDiario.value}&end_date=${endDateDiario.value}&format=json`)
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Error al generar el reporte');
      }
      const data = await response.json()
      diarioReportData.value = data.data
    } else {
      const response = await fetch(`${apiUrl}/reports/diario?start_date=${startDateDiario.value}&end_date=${endDateDiario.value}`)
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Error al generar el reporte');
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      
      const a = document.createElement('a')
      a.href = url
      a.download = `Libro_Diario_${startDateDiario.value}_to_${endDateDiario.value}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const generateDiarioExcel = async (preview: boolean = false) => {
  loading.value = true
  error.value = ''
  reportType.value = 'DIARIO_EXCEL'
  
  try {
    const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
    const formatParam = preview ? 'format=json' : ''
    const endpoint = preview ? 'reports/diario' : 'reports/diario_excel'
    const separator = preview ? '&' : '?'
    
    const response = await fetch(`${apiUrl}/${endpoint}?start_date=${startDateDiario.value}&end_date=${endDateDiario.value}${preview ? '&format=json' : ''}`)
    
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Error al procesar el reporte');
    }
    
    if (preview) {
      const result = await response.json()
      diarioReportData.value = result.data
    } else {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Libro_Diario_${startDateDiario.value}_to_${endDateDiario.value}.xlsx`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const generateBG = async (preview = false) => {
  loading.value = true
  error.value = ''
  reportData.value = []
  erReportData.value = null
  diarioReportData.value = null
  bgReportData.value = null
  reportType.value = 'BG'

  try {
    const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : ''

    if (preview) {
      const response = await fetch(`${apiUrl}/reports/balance-general?start_date=${bgStartDate.value}&end_date=${bgEndDate.value}&format=json`)
      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Error al generar el reporte')
      }
      const result = await response.json()
      bgReportData.value = result.data
    } else {
      const response = await fetch(`${apiUrl}/reports/balance-general?start_date=${bgStartDate.value}&end_date=${bgEndDate.value}`)
      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Error al generar el reporte')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Balance_General_${bgStartDate.value}_${bgEndDate.value}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="reports-page">
    <PageHero
      title="Centro de Reportes"
      subtitle="Genera reportes oficiales firmados con formato profesional"
      gradient="linear-gradient(135deg, #7c2d12 0%, #c2410c 45%, #fb923c 100%)"
    />

    <div class="report-grid">
      <div class="report-card primary">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        </div>
        <div class="card-content">
          <h3>Balance de Sumas y Saldos (BSS)</h3>
          <p>Estado financiero que muestra los saldos de todas las cuentas del mayor hasta una fecha de corte, agrupados por niveles jerárquicos.</p>
          
          <div class="report-actions">
            <div class="field">
              <label>Fecha de Corte:</label>
              <input type="date" v-model="endDate">
            </div>
            <div class="action-buttons">
                <button @click="generateBSS(true)" :disabled="loading" class="btn-generate secondary">
                  <span v-if="loading">Cargando...</span>
                  <span v-else>Ver Pantalla</span>
                </button>
                <button @click="generateBSS(false)" :disabled="loading" class="btn-generate">
                  <span v-if="loading">Generando...</span>
                  <span v-else>Descargar PDF</span>
                </button>
            </div>
          </div>
          
          <div v-if="error && reportType === 'BSS'" class="error-box">
             {{ error }}
          </div>
        </div>
      </div>

      <div class="report-card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>
        </div>
        <div class="card-content">
          <h3>Estado de Resultados (ER)</h3>
          <p>Estado financiero que muestra los ingresos, costos y gastos de la empresa, determinando el resultado final (utilidad o pérdida) en un periodo dado.</p>
          
          <div class="report-actions">
            <div class="field">
              <label>Fecha de Corte:</label>
              <input type="date" v-model="endDate">
            </div>
            <div class="action-buttons">
                <button @click="generateER" :disabled="loading" class="btn-generate secondary">
                  <span v-if="loading && reportType === 'ER'">Cargando...</span>
                  <span v-else>Ver Pantalla</span>
                </button>
            </div>
          </div>
          <div v-if="error && reportType === 'ER'" class="error-box">
             {{ error }}
          </div>
        </div>
      </div>

      <div class="report-card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
        </div>
        <div class="card-content">
          <h3>Libro Diario General</h3>
          <p>Listado correlativo y cronológico de todos los asientos o comprobantes contables registrados en el periodo.</p>
          
          <div class="report-actions">
            <div class="field">
              <label>Desde:</label>
              <input type="date" v-model="startDateDiario">
            </div>
            <div class="field">
              <label>Hasta:</label>
              <input type="date" v-model="endDateDiario">
            </div>
            <div class="action-buttons">
                <button @click="generateDiario(true)" :disabled="loading" class="btn-generate secondary">
                  <span v-if="loading && reportType === 'DIARIO'">Cargando...</span>
                  <span v-else>Ver Pantalla (Oficial)</span>
                </button>
                <button @click="generateDiarioExcel(true)" :disabled="loading" class="btn-generate secondary excel-preview">
                  <span v-if="loading && reportType === 'DIARIO_EXCEL' && diarioReportData">Cargando...</span>
                  <span v-else>Ver Pantalla (Excel)</span>
                </button>
                <button @click="generateDiario(false)" :disabled="loading" class="btn-generate">
                  <span v-if="loading && reportType === 'DIARIO'">Generando...</span>
                  <span v-else>Descargar PDF</span>
                </button>
                <button @click="generateDiarioExcel(false)" :disabled="loading" class="btn-generate excel">
                  <span v-if="loading && reportType === 'DIARIO_EXCEL'">Generando...</span>
                  <span v-else>Descargar Excel</span>
                </button>
            </div>
          </div>
          <div v-if="error && reportType === 'DIARIO'" class="error-box">
             {{ error }}
          </div>
        </div>
      </div>

      <!-- Balance General Card -->
      <div class="report-card">
        <div class="card-icon" style="color: #0f766e;">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="card-content">
          <h3>Balance General (BG)</h3>
          <p>Estado de situación financiera que muestra los activos, pasivos y patrimonio de la empresa estructurado por cuentas jerárquicas a una fecha de corte.</p>

          <div class="report-actions">
            <div class="field">
              <label>Desde:</label>
              <input type="date" v-model="bgStartDate">
            </div>
            <div class="field">
              <label>Hasta:</label>
              <input type="date" v-model="bgEndDate">
            </div>
            <div class="action-buttons">
              <button @click="generateBG(true)" :disabled="loading" class="btn-generate secondary">
                <span v-if="loading && reportType === 'BG'">Cargando...</span>
                <span v-else>Ver Pantalla</span>
              </button>
              <button @click="generateBG(false)" :disabled="loading" class="btn-generate">
                <span v-if="loading && reportType === 'BG'">Generando...</span>
                <span v-else>Descargar PDF</span>
              </button>
            </div>
          </div>
          <div v-if="error && reportType === 'BG'" class="error-box">
            {{ error }}
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="reportData.length > 0" class="html-report-container">
        <div class="preview-header">
            <h3>SISTEMA CONTABLE SIC4BUS - Balance de Sumas y Saldos</h3>
            <div>
              <span class="report-date">Al {{ endDate.split('-').reverse().join('/') }}</span>
              <button @click="reportData = []" class="btn-close">Cerrar</button>
            </div>
        </div>
        
        <div class="table-responsive">
          <table class="report-table">
            <thead>
              <tr>
                <th>CÓDIGO</th>
                <th>CUENTA</th>
                <th class="num">DEBE</th>
                <th class="num">HABER</th>
                <th class="num">DEUDOR</th>
                <th class="num">ACREEDOR</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in reportData" :key="row.code" :class="{'parent-account': row.level < 5}">
                <td>{{ row.code }}</td>
                <td>{{ row.name }}</td>
                <td class="num">{{ Number(row.debit).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="num">{{ Number(row.credit).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="num">{{ Number(row.deudor).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="num">{{ Number(row.acreedor).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
              </tr>
              <tr class="total-row">
                <td colspan="2" style="text-align: center; font-weight: bold;">TOTALES</td>
                <td class="num" style="font-weight: bold; border-top: 2px solid var(--border);">{{ totalBSS.debit.toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="num" style="font-weight: bold; border-top: 2px solid var(--border);">{{ totalBSS.credit.toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="num" style="font-weight: bold; border-top: 2px solid var(--border);">{{ totalBSS.deudor.toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="num" style="font-weight: bold; border-top: 2px solid var(--border);">{{ totalBSS.acreedor.toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
    </div>
    
    <!-- ER HTML Report Container -->
    <div v-if="erReportData" class="html-report-container">
        <div class="preview-header">
            <h3>SISTEMA CONTABLE SIC4BUS - Estado de Resultados</h3>
            <div>
              <span class="report-date">Al {{ endDate.split('-').reverse().join('/') }}</span>
              <button @click="erReportData = null" class="btn-close">Cerrar</button>
            </div>
        </div>
        
        <div class="table-responsive">
          <table class="report-table er-table">
            <thead>
              <tr>
                <th>CÓDIGO</th>
                <th>CUENTA</th>
                <th class="num">IMPORTE</th>
              </tr>
            </thead>
            <tbody>
              <!-- Ingresos -->
              <tr class="section-title">
                <td colspan="3">INGRESOS</td>
              </tr>
              <tr v-for="row in erReportData.ingresos" :key="row.code" :class="{'parent-account': row.level < 5, 'level-1': row.level === 1}">
                <td>{{ row.code }}</td>
                <td :style="{ paddingLeft: `${(row.level - 1) * 1.5 + 1}rem` }">{{ row.name }}</td>
                <td class="num">{{ Number(row.amount).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
              </tr>
              <tr class="total-row positive">
                <td colspan="2">TOTAL INGRESOS</td>
                <td class="num">{{ Number(erReportData.total_ingresos).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
              </tr>
              
              <!-- Egresos -->
              <tr class="section-title">
                <td colspan="3">EGRESOS (COSTOS Y GASTOS)</td>
              </tr>
              <tr v-for="row in erReportData.egresos" :key="row.code" :class="{'parent-account': row.level < 5, 'level-1': row.level === 1}">
                <td>{{ row.code }}</td>
                <td :style="{ paddingLeft: `${(row.level - 1) * 1.5 + 1}rem` }">{{ row.name }}</td>
                <td class="num">{{ Number(row.amount).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
              </tr>
              <tr class="total-row negative">
                <td colspan="2">TOTAL EGRESOS</td>
                <td class="num">{{ Number(erReportData.total_egresos).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
              </tr>
              
              <!-- Resultado Final -->
              <tr class="final-result-row">
                <td colspan="2">RESULTADO DEL EJERCICIO</td>
                <td class="num" :class="erReportData.resultado >= 0 ? 'text-positive' : 'text-negative'">
                    {{ Number(erReportData.resultado).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
    </div>

    <!-- Libro Diario HTML Report Container -->
    <div v-if="diarioReportData" class="html-report-container">
        <div class="preview-header">
            <h3>VISUALIZACIÓN DE REPORTE - {{ reportType === 'DIARIO_EXCEL' ? 'LIBRO DIARIO (EXCEL)' : 'LIBRO DIARIO (OFICIAL)' }}</h3>
            <button @click="diarioReportData = null" class="btn-close">Cerrar</button>
        </div>
        
        <div class="table-responsive">
          <!-- Format: Official (PDF-like) -->
          <table v-if="reportType === 'DIARIO'" class="report-table diario-table">
            <thead>
              <tr>
                <th style="width: 100px;">FECHA</th>
                <th style="width: 120px;">CÓDIGO</th>
                <th>DETALLE</th>
                <th class="num" style="width: 120px;">DEBE</th>
                <th class="num" style="width: 120px;">HABER</th>
              </tr>
            </thead>
            <tbody v-for="entry in diarioReportData" :key="entry.id">
              <tr class="entry-header-row">
                <td class="text-center">{{ entry.date.split('T')[0].split('-').reverse().join('/') }}</td>
                <td></td>
                <td class="bold">COMPROBANTE DE {{ getVoucherTypeName(entry.entry_type) }} Nro. :{{ entry.entry_number || entry.id }}</td>
                <td></td>
                <td></td>
              </tr>
              <tr v-for="detail in entry.details" :key="detail.account.code + detail.debit + detail.credit" class="detail-row">
                <td></td>
                <td>{{ detail.account.code }}</td>
                <td :class="{'indented': detail.credit > 0}">{{ detail.account.name }}</td>
                <td class="num">{{ detail.debit > 0 ? Number(detail.debit).toLocaleString('en-US', {minimumFractionDigits: 2}) : '' }}</td>
                <td class="num">{{ detail.credit > 0 ? Number(detail.credit).toLocaleString('en-US', {minimumFractionDigits: 2}) : '' }}</td>
              </tr>
              <tr class="entry-footer-row">
                <td></td>
                <td></td>
                <td class="italic">{{ entry.description }}</td>
                <td class="num bold border-top-double">{{ entry.details.reduce((sum: number, d: any) => sum + d.debit, 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
                <td class="num bold border-top-double">{{ entry.details.reduce((sum: number, d: any) => sum + d.credit, 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
              </tr>
              <tr class="spacer-row"><td colspan="5"></td></tr>
            </tbody>
            <tfoot>
              <tr class="final-total-row">
                <td colspan="3" class="text-right bold">TOTAL GENERAL DEL DIARIO</td>
                <td class="num bold">{{ diarioReportData.reduce((total, entry) => total + entry.details.reduce((sum: number, d: any) => sum + d.debit, 0), 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
                <td class="num bold">{{ diarioReportData.reduce((total, entry) => total + entry.details.reduce((sum: number, d: any) => sum + d.credit, 0), 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
              </tr>
            </tfoot>
          </table>

          <!-- Format: Excel (Sequential spreadsheet-style) -->
          <div v-if="reportType === 'DIARIO_EXCEL'" class="excel-preview-wrapper">
            <div class="excel-report-header">
              <div class="company-info">
                <strong>COMSATELITAL S.R.L.</strong><br>
                LA PAZ - BOLIVIA
              </div>
              <div class="report-title">
                <h2>LIBRO DIARIO</h2>
                <p>Del {{ startDateDiario.split('-').reverse().join('/') }} al {{ endDateDiario.split('-').reverse().join('/') }}</p>
                <p>(Expresado en Bolivianos)</p>
              </div>
              <div class="currency-label">BOLIVIANOS</div>
            </div>

            <table class="report-table excel-style-table">
              <thead>
                <tr>
                  <th class="text-center">Nro</th>
                  <th class="text-center">Tipo</th>
                  <th class="text-center">Fecha</th>
                  <th class="text-center">Código</th>
                  <th>Detalle</th>
                  <th class="num">Debe</th>
                  <th class="num">Haber</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(entry, index) in diarioReportData" :key="entry.id">
                  <!-- Sequential Entry Row -->
                  <tr class="excel-entry-start">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td class="text-center">{{ entry.entry_type }}</td>
                    <td class="text-center">{{ entry.date.split('T')[0].split('-').reverse().join('/') }}</td>
                    <td></td>
                    <td class="bold">COMPROBANTE DE {{ getVoucherTypeName(entry.entry_type) }} Nro. :{{ entry.entry_number || entry.id }}</td>
                    <td></td>
                    <td></td>
                  </tr>
                  <!-- Detail Rows (one for each accounting line) -->
                  <tr v-for="detail in entry.details" :key="detail.account.code + detail.debit + detail.credit" class="excel-detail-row">
                    <td></td>
                    <td></td>
                    <td></td>
                    <td class="text-center">{{ detail.account.code }}</td>
                    <td>{{ detail.account.name }}</td>
                    <td class="num">{{ detail.debit > 0 ? Number(detail.debit).toLocaleString('en-US', {minimumFractionDigits: 2}) : '' }}</td>
                    <td class="num">{{ detail.credit > 0 ? Number(detail.credit).toLocaleString('en-US', {minimumFractionDigits: 2}) : '' }}</td>
                  </tr>
                  <!-- Glosa and Subtotals Row -->
                  <tr class="excel-glosa-row">
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td class="italic">{{ entry.description }}</td>
                    <td class="num bold">{{ entry.details.reduce((sum: number, d: any) => sum + d.debit, 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
                    <td class="num bold">{{ entry.details.reduce((sum: number, d: any) => sum + d.credit, 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
                  </tr>
                  <!-- Optional spacer line like in Excel -->
                  <tr class="excel-spacer">
                    <td colspan="7"></td>
                  </tr>
                </template>
              </tbody>
              <tfoot>
                <tr class="excel-total-row">
                  <td colspan="5" class="text-right bold">TOTAL GENERAL DEL DIARIO</td>
                  <td class="num bold underline">{{ diarioReportData.reduce((total, entry) => total + entry.details.reduce((sum: number, d: any) => sum + d.debit, 0), 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
                  <td class="num bold underline">{{ diarioReportData.reduce((total, entry) => total + entry.details.reduce((sum: number, d: any) => sum + d.credit, 0), 0).toLocaleString('en-US', {minimumFractionDigits: 2}) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
    </div>

    <!-- Balance General HTML Preview -->
    <div v-if="bgReportData" class="html-report-container">
      <div class="preview-header">
        <h3>COMSATELITAL S.R.L. — Balance General</h3>
        <div>
          <span class="report-date">Del {{ bgStartDate.split('-').reverse().join('/') }} al {{ bgEndDate.split('-').reverse().join('/') }}</span>
          <button @click="bgReportData = null" class="btn-close">Cerrar</button>
        </div>
      </div>

      <div class="bg-report-body">
        <!-- ACTIVO -->
        <div class="bg-section">
          <div class="bg-section-title">CUENTAS DE ACTIVO</div>
          <table class="report-table bg-table">
            <thead>
              <tr>
                <th style="width:160px">CODIGO</th>
                <th>NOMBRE</th>
                <th class="num" style="width:160px">BOLIVIANOS Bs.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in bgReportData.activo" :key="row.code"
                  :class="{
                    'bg-level-1': row.level === 1,
                    'bg-level-2': row.level === 2,
                    'bg-level-3': row.level === 3,
                    'bg-level-4': row.level === 4,
                    'bg-level-5': row.level === 5
                  }">
                <td>{{ row.code }}</td>
                <td :style="{ paddingLeft: `${(row.level - 1) * 1.5 + 0.75}rem` }">{{ row.name }}</td>
                <td class="num">{{ row.balance !== 0 ? Number(row.balance).toLocaleString('es-PE', {minimumFractionDigits:2, maximumFractionDigits:2}) : '' }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="bg-total-row">
                <td colspan="2">TOTAL CUENTAS DE ACTIVO</td>
                <td class="num">{{ Number(bgReportData.total_activo).toLocaleString('es-PE', {minimumFractionDigits:2, maximumFractionDigits:2}) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- PASIVO Y PATRIMONIO -->
        <div class="bg-section" style="margin-top:2rem">
          <div class="bg-section-title">CUENTAS DE PASIVO Y PATRIMONIO</div>
          <table class="report-table bg-table">
            <thead>
              <tr>
                <th style="width:160px">CODIGO</th>
                <th>NOMBRE</th>
                <th class="num" style="width:160px">BOLIVIANOS Bs.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in bgReportData.pasivo_patrimonio" :key="row.code"
                  :class="{
                    'bg-level-1': row.level === 1,
                    'bg-level-2': row.level === 2,
                    'bg-level-3': row.level === 3,
                    'bg-level-4': row.level === 4,
                    'bg-level-5': row.level === 5
                  }">
                <td>{{ row.code }}</td>
                <td :style="{ paddingLeft: `${(row.level - 1) * 1.5 + 0.75}rem` }">{{ row.name }}</td>
                <td class="num">{{ row.balance !== 0 ? Number(row.balance).toLocaleString('es-PE', {minimumFractionDigits:2, maximumFractionDigits:2}) : '' }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="bg-total-row">
                <td colspan="2">TOTAL CUENTAS DE PASIVO Y PATRIMONIO</td>
                <td class="num">{{ Number(bgReportData.total_pasivo_patrimonio).toLocaleString('es-PE', {minimumFractionDigits:2, maximumFractionDigits:2}) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reports-page {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 3rem;
}

h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-muted);
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(450px, 100%), 1fr));
  gap: 2rem;
}

@media (max-width: 600px) {
  .report-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

.report-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  gap: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.report-card.primary:hover {
  border-color: var(--primary-light);
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.report-card.disabled {
  opacity: 0.6;
  background: var(--bg);
}

.card-icon {
  width: 64px;
  height: 64px;
  background: var(--bg);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  flex-shrink: 0;
}

.report-card.disabled .card-icon {
  color: var(--text-muted);
}

.card-content h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.card-content p {
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.report-actions {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  background: var(--bg);
  padding: 1.25rem;
  border-radius: 12px;
  flex-wrap: wrap;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.field label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
}

input[type="date"] {
  border: 1px solid var(--border);
  padding: 0.5rem;
  border-radius: 6px;
  font-family: inherit;
  font-size: 1rem;
}

.btn-generate {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  height: 42px;
  transition: filter 0.2s;
}

.btn-generate.secondary {
    background: white;
    color: var(--primary);
    border: 1px solid var(--primary);
}

.btn-generate:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn-generate.secondary:hover:not(:disabled) {
    background: #f8fafc;
}

.btn-generate.secondary:hover:not(:disabled) {
    background: #f8fafc;
}

.btn-generate.excel {
    background: #166534;
    color: white;
}

.btn-generate.excel-preview {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
}

.btn-generate.excel-preview:hover {
    background: #dcfce7;
}

.btn-generate:disabled {
  background: var(--text-muted);
  color: white;
  border: none;
  cursor: not-allowed;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.error-box {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 8px;
  font-size: 0.9rem;
}

/* HTML Preview */
.html-report-container {
    margin-top: 3rem;
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: #f8fafc;
    border-bottom: 1px solid var(--border);
}

.preview-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--text);
    font-weight: 700;
}

.report-date {
    margin-right: 1.5rem;
    color: var(--text-muted);
    font-weight: 500;
}

.btn-close {
    background: transparent;
    border: 1px solid var(--border);
    padding: 0.4rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    color: var(--text-muted);
    transition: all 0.2s;
}

.btn-close:hover {
    background: #e2e8f0;
    color: var(--text);
}

.table-responsive {
    overflow-x: auto;
    padding: 1rem;
}

.report-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.report-table th, .report-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
}

.report-table th {
    background: #f1f5f9;
    font-weight: 700;
    color: var(--text);
    text-transform: uppercase;
    font-size: 0.8rem;
}

.report-table th.num, .report-table td.num {
    text-align: right;
    font-variant-numeric: tabular-nums;
}

.report-table tr:hover {
    background: #f8fafc;
}

.report-table tr.parent-account td {
    font-weight: 700;
    color: var(--text);
    background: #fcfcfc;
}

/* ER Specific Styling */
.er-table .section-title td {
    background: var(--primary);
    color: white;
    font-weight: 800;
    text-transform: uppercase;
    padding: 0.5rem 1rem;
}

.er-table tr.level-1 td {
    background: #e2e8f0;
    font-weight: 800;
}

/* Diario Specific Styling */
.diario-table .entry-header-row td {
    background: #f8fafc;
    border-top: 1px solid var(--border);
}

.diario-table .bold { font-weight: 700; }
.diario-table .italic { font-style: italic; color: #4b5563; }
.diario-table .text-center { text-align: center; }
.diario-table .text-right { text-align: right; }

.diario-table .detail-row td {
    border-bottom: none;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
}

.diario-table .indented {
    padding-left: 2rem !important;
}

.diario-table .entry-footer-row td {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1rem;
}

.diario-table .border-top-double {
    border-top: 3px double var(--border);
}

.diario-table .spacer-row td {
    padding: 0.5rem;
    border: none;
}

.diario-table .final-total-row td {
    background: #f1f5f9;
    font-size: 1rem;
    padding: 1.25rem 1rem;
    border-top: 2px solid var(--text);
}

.er-table .total-row td {
    font-weight: 800;
    font-size: 1.05rem;
    padding: 1rem;
    border-top: 2px solid var(--border);
}

.er-table .total-row.positive td {
    background: #f0fdf4;
    color: #166534;
}

.er-table .total-row.negative td {
    background: #fef2f2;
    color: #991b1b;
}

.er-table .final-result-row td {
    background: #f8fafc;
    font-weight: 900;
    font-size: 1.2rem;
    padding: 1.25rem 1rem;
    text-transform: uppercase;
    border-top: 3px double var(--border);
}

.text-positive { color: #15803d; }
.text-negative { color: #b91c1c; }

/* Excel Preview Specific */
.excel-preview-wrapper {
    padding: 2rem;
    background: white;
}

.excel-report-header {
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
}

.excel-report-header .company-info {
    position: absolute;
    left: 0;
    top: 0;
    text-align: left;
    font-size: 0.9rem;
}

.excel-report-header .report-title h2 {
    font-size: 1.5rem;
    margin: 0;
    font-weight: 800;
}

.excel-report-header .report-title p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}

.excel-report-header .currency-label {
    position: absolute;
    right: 5%;
    bottom: -1.5rem;
    font-weight: 700;
    font-size: 0.8rem;
}

.excel-style-table {
    border: 1px solid #000;
    border-collapse: collapse;
}

.excel-style-table th {
    background: #f1f5f9;
    color: #000;
    font-weight: 700;
    border: 1px solid #000;
    padding: 0.4rem;
    text-transform: none;
}

.excel-style-table td {
    border: 1px solid #e2e8f0;
    padding: 0.3rem 0.5rem !important;
}

.excel-entry-start td {
    background: #fff;
    border-top: 1px solid #000;
}

.excel-detail-row td {
    background: white;
}

.excel-glosa-row td {
    background: #fff;
}

.excel-total-row td {
    background: #fff !important;
    color: #000 !important;
    border-top: 1px solid #000;
    border-bottom: 1px solid #000;
}

.excel-spacer td {
    height: 1rem;
    border: none !important;
}

.underline {
    text-decoration: underline;
    text-underline-offset: 4px;
}

/* ====== Balance General styles ====== */
.bg-report-body {
  padding: 1.5rem;
}

.bg-section-title {
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text);
  padding: 0.5rem 0;
  margin-bottom: 0.5rem;
  border-bottom: 2px solid var(--border);
  letter-spacing: 0.05em;
}

.bg-table {
  font-size: 0.85rem;
}

.bg-level-1 td {
  font-weight: 700;
  font-size: 0.9rem;
  background: #f8fafc;
}

.bg-level-2 td {
  font-weight: 600;
}

.bg-level-3 td {
  font-weight: 500;
}

.bg-level-4 td,
.bg-level-5 td {
  font-weight: 400;
  color: #475569;
}

.bg-total-row td {
  font-weight: 700;
  font-size: 0.9rem;
  border-top: 2px solid #1e40af;
  padding-top: 0.75rem;
  background: #eff6ff;
}
</style>
