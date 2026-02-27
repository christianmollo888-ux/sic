<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { systemService } from '../services/api'
import PageHero from '../components/PageHero.vue'

const capacityStats = ref<Record<string, number>>({})
const totalsComparison = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const [capRes, totalRes] = await Promise.all([
      systemService.getCapacityStats(),
      systemService.getTotalsComparison()
    ])
    capacityStats.value = capRes.data
    totalsComparison.value = totalRes.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function formatCurrency(val: number) {
  return new Intl.NumberFormat('es-BO', { style: 'currency', currency: 'BOB' }).format(val)
}
function formatNumber(val: number) {
  return new Intl.NumberFormat('es-BO').format(val)
}
</script>

<template>
  <div class="stats-page">
    <PageHero
      title="Estadísticas y Capacidad"
      subtitle="Validación de integridad de datos y uso de tablas"
      gradient="linear-gradient(135deg, #064e3b 0%, #059669 50%, #10b981 100%)"
    />

    <div v-if="loading" class="loading-block">
      <div class="spinner-global"></div>
      <span>Analizando base de datos...</span>
    </div>

    <div v-else class="stats-grid">
      <!-- Capacity Card -->
      <div class="card capacity-card">
        <div class="card-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
          <div>
            <h3>Capacidad de Tablas</h3>
            <p>Conteo de registros por tabla física</p>
          </div>
        </div>
        <div class="stat-list">
          <div v-for="(count, table) in capacityStats" :key="table" class="stat-row">
            <span class="table-name">{{ table }}</span>
            <span class="table-count">{{ formatNumber(count) }}</span>
          </div>
        </div>
      </div>

      <!-- Totals Comparison Card -->
      <div v-if="totalsComparison" class="card comparison-card">
        <div class="card-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
          <div>
            <h3>Validación de Totales</h3>
            <p>Comparativo Legacy vs Sistema Moderno</p>
          </div>
        </div>

        <div class="table-wrap">
          <table class="premium-table">
            <thead>
              <tr>
                <th>Métrica</th>
                <th>Legacy</th>
                <th>Moderno</th>
                <th>Diferencia</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Total Debe</td>
                <td>{{ formatCurrency(totalsComparison.legacy.debit) }}</td>
                <td>{{ formatCurrency(totalsComparison.modern.debit) }}</td>
                <td :class="Math.abs(totalsComparison.difference.debit) < 0.01 ? 'ok' : 'err'">
                  {{ formatCurrency(totalsComparison.difference.debit) }}
                </td>
              </tr>
              <tr>
                <td>Total Haber</td>
                <td>{{ formatCurrency(totalsComparison.legacy.credit) }}</td>
                <td>{{ formatCurrency(totalsComparison.modern.credit) }}</td>
                <td :class="Math.abs(totalsComparison.difference.credit) < 0.01 ? 'ok' : 'err'">
                  {{ formatCurrency(totalsComparison.difference.credit) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="Math.abs(totalsComparison.difference.debit) < 0.01 && Math.abs(totalsComparison.difference.credit) < 0.01" class="alert alert-success">
          ✅ ¡Validación exitosa! Los datos se han transferido íntegramente.
        </div>
        <div v-else class="alert alert-warning">
          ⚠️ Se detectaron discrepancias. Revisar el script de migración.
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-page { max-width: 1200px; margin: 0 auto; }

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
}
@media (max-width: 900px) { .stats-grid { grid-template-columns: 1fr; } }

.card-header {
  display: flex; gap: 0.85rem; align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
.card-header svg { color: var(--primary); margin-top: 2px; flex-shrink: 0; }
.card-header h3 { margin: 0 0 0.2rem; font-size: 1.05rem; font-weight: 700; }
.card-header p { margin: 0; font-size: 0.82rem; color: var(--text-muted); }

/* Capacity list */
.stat-list { display: flex; flex-direction: column; gap: 0.6rem; }
.stat-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: #f8fafc;
  transition: background 0.15s;
}
.stat-row:hover { background: #eff6ff; }
.table-name { font-weight: 600; color: var(--text); font-size: 0.85rem; }
.table-count {
  font-family: monospace; font-weight: 800; font-size: 0.9rem;
  color: var(--primary);
  background: #dbeafe; padding: 0.15rem 0.5rem; border-radius: 6px;
}

/* Table utilities */
.table-wrap { margin-bottom: 1.25rem; border-radius: 10px; border: 1px solid var(--border); overflow-x: auto; }
.ok { color: #059669; font-weight: 700; }
.err { color: var(--danger); font-weight: 700; }
</style>
