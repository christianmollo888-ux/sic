<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  show: boolean
  title: string
  reportData: any
}>()

const emit = defineEmits(['close'])

const months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

// Field codes to display in the header (matching the Excel template)
const fieldCodes = [
  '13', '14', '15', '505', '16', '17', '18', '39', '55', '19', '1002', '11', '26', '31', '27', '28', '114', '30', '1003', '1004', '693', '909', '635', '648', '1001', '621', '629', '622', '640', '643', '468', '465', '466', '467', '996', '924', '925', '938', '954', '967', '955', '592', '469', '747', '646', '677', '678', '576', '580', '581'
]

// Mapping for summary columns at the end
const summaryLabels = [
  { label: "IVA FISCO", code: "909" },
  { label: "IVA CONTRIB", code: "693" },
  { label: "MES ANT", code: "635" },
  { label: "MNTTO VAL", code: "648" },
  { label: "A PAGAR", code: "1001" },
  { label: "SIG MES", code: "592" }
]

const formatCurrency = (val: number) => {
  if (isNaN(val) || val === 0) return '-'
  return new Intl.NumberFormat('es-BO', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(val)
}

const getCellValue = (monthIdx: number, fieldCode: string) => {
  if (!props.reportData) return 0
  const cleanFieldCode = String(fieldCode).replace('C', '').trim()
  const row = props.reportData.rows.find((r: any) => {
    const rowCode = String(r.field_code).replace('C', '').replace('Casilla', '').trim()
    return rowCode === cleanFieldCode
  })
  if (!row) return 0
  const val = row.months[monthIdx]
  return Number(val) || 0
}

const getColumnTotal = (fieldCode: string) => {
  if (!props.reportData) return 0
  const cleanFieldCode = String(fieldCode).replace('C', '').trim()
  const row = props.reportData.rows.find((r: any) => {
    const rowCode = String(r.field_code).replace('C', '').replace('Casilla', '').trim()
    return rowCode === cleanFieldCode
  })
  if (!row) return 0
  return row.months.reduce((acc: number, val: any) => {
    const num = Number(val) || 0
    return acc + num
  }, 0)
}
</script>

<template>
  <div v-if="show" class="modal-backdrop" @click="emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="header-left">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="header-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          <h2>{{ title }}</h2>
        </div>
        <button class="close-btn" @click="emit('close')">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="table-wrapper">
          <table class="preview-table">
            <thead>
              <tr class="code-row">
                <th class="sticky-col">MES</th>
                <th v-for="code in fieldCodes" :key="code">C{{ code }}</th>
                <th v-for="item in summaryLabels" :key="item.code" class="summary-header">{{ item.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(month, idx) in months" :key="month">
                <td class="sticky-col month-name">{{ month }}</td>
                <td v-for="code in fieldCodes" :key="code" class="val-cell">
                  {{ formatCurrency(getCellValue(idx, code)) }}
                </td>
                <td v-for="item in summaryLabels" :key="item.code" class="val-cell summary-cell">
                  {{ formatCurrency(getCellValue(idx, item.code)) }}
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="total-row">
                <td class="sticky-col total-label">TOTAL</td>
                <td v-for="code in fieldCodes" :key="code" class="val-cell total-val">
                  {{ formatCurrency(getColumnTotal(code)) }}
                </td>
                <td v-for="item in summaryLabels" :key="item.code" class="val-cell total-val summary-cell">
                  {{ formatCurrency(getColumnTotal(item.code)) }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      
      <div class="modal-footer">
        <p class="footer-note">Cifras expresadas en Bolivianos (Bs.). Basado en declaraciones procesadas.</p>
        <button class="btn btn-secondary" @click="emit('close')">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 2rem;
}
.modal-container {
  background: white; border-radius: 16px; width: 100%; max-width: 95vw;
  max-height: 90vh; display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
.modal-header {
  padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0;
  display: flex; justify-content: space-between; align-items: center;
  background: #f8fafc;
}
.header-left { display: flex; align-items: center; gap: 0.75rem; }
.header-icon { color: #059669; }
.modal-header h2 { margin: 0; font-size: 1.25rem; font-weight: 700; color: #1e293b; }
.close-btn {
  background: none; border: none; font-size: 1.75rem; color: #64748b;
  cursor: pointer; padding: 0.25rem; line-height: 1; transition: color 0.2s;
}
.close-btn:hover { color: #1e293b; }

.modal-body { flex: 1; overflow: hidden; padding: 0; }
.table-wrapper { overflow: auto; height: 100%; max-height: 70vh; }

.preview-table { border-collapse: separate; border-spacing: 0; width: 100%; font-size: 0.75rem; }
.preview-table th {
  background: #f1f5f9; color: #475569; position: sticky; top: 0;
  padding: 0.75rem 0.5rem; font-weight: 700; border-bottom: 2px solid #e2e8f0;
  border-right: 1px solid #e2e8f0; text-align: center; z-index: 10;
}
.summary-header { background: #ecfdf5 !important; color: #065f46 !important; }
.sticky-col { position: sticky; left: 0; background: #f8fafc; z-index: 20; border-right: 2px solid #e2e8f0 !important; }

.preview-table td { padding: 0.5rem; border-bottom: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9; }
.month-name { font-weight: 600; color: #1e293b; background: #f8fafc; }
.val-cell { text-align: right; font-family: 'Inter', monospace; color: #475569; min-width: 60px; }
.summary-cell { background: #f9fafb; font-weight: 600; color: #059669; }

.preview-table tr:hover td { background: #f1f5f9; }

tfoot { position: sticky; bottom: 0; z-index: 10; }
.total-row td { background: #f8fafc; border-top: 2px solid #e2e8f0; font-weight: 800; color: #1e293b; }
.total-label { z-index: 21; }
.total-val { border-top: 2px solid #cbd5e1 !important; color: #0f172a !important; }

.modal-footer {
  padding: 1rem 1.5rem; border-top: 1px solid #e2e8f0;
  display: flex; justify-content: space-between; align-items: center;
  background: #f8fafc;
}
.footer-note { margin: 0; font-size: 0.8rem; color: #64748b; font-style: italic; }
</style>
