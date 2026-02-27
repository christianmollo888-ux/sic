<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { systemService } from '../services/api'

const tables = ref<string[]>([])
const selectedTable = ref('')
const tableData = ref<any[]>([])
const loading = ref(false)
const skip = ref(0)
const limit = 50

onMounted(async () => {
  const res = await systemService.getTables()
  tables.value = res.data
  if (tables.value.length > 0) {
    selectedTable.value = tables.value[0]
  }
})

async function fetchTableData() {
  if (!selectedTable.value) return
  loading.value = true
  try {
    const res = await systemService.getTableData(selectedTable.value, skip.value, limit)
    tableData.value = res.data
  } catch (e) {
    console.error(e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

watch(selectedTable, () => {
  skip.value = 0
  fetchTableData()
})

function next() {
  skip.value += limit
  fetchTableData()
}

function prev() {
  skip.value = Math.max(0, skip.value - limit)
  fetchTableData()
}

const columns = ref<string[]>([])
watch(tableData, (newData) => {
  if (newData.length > 0) {
    columns.value = Object.keys(newData[0])
  } else {
    columns.value = []
  }
})
</script>

<template>
  <div>
    <div class="header-section">
      <h1>Inspector de Datos</h1>
      <p class="text-muted">Visualización directa de tablas legacy y modernas.</p>
    </div>

    <div class="controls card">
      <div class="select-group">
        <label>Seleccionar Tabla:</label>
        <select v-model="selectedTable">
          <option v-for="table in tables" :key="table" :value="table">{{ table }}</option>
        </select>
      </div>
      <div class="pagination">
        <button @click="prev" :disabled="skip === 0" class="btn">Anterior</button>
        <span class="page-info">Registros {{ skip }} - {{ skip + tableData.length }}</span>
        <button @click="next" :disabled="tableData.length < limit" class="btn">Siguiente</button>
      </div>
    </div>

    <div v-if="loading" class="card">Cargando datos de {{ selectedTable }}...</div>
    <div v-else-if="tableData.length === 0" class="card">No hay datos para mostrar.</div>
    <div v-else class="card table-container">
      <table class="inspector-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in tableData" :key="idx">
            <td v-for="col in columns" :key="col">
                <span :class="{ 'mono': typeof row[col] === 'string' }">{{ row[col] }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.header-section { margin-bottom: 2rem; }
.controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding: 1rem 1.5rem; }
.select-group { display: flex; align-items: center; gap: 1rem; }
select { padding: 0.5rem; border-radius: 8px; border: 1px solid #e2e8f0; min-width: 200px; font-weight: 600; }
.pagination { display: flex; align-items: center; gap: 1rem; }
.page-info { font-weight: 600; color: #64748b; font-size: 0.875rem; }

.table-container { padding: 0; overflow: auto; max-height: 70vh; border-radius: 12px; }
.inspector-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.inspector-table th { background: #f8fafc; position: sticky; top: 0; padding: 0.75rem 1rem; text-align: left; border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: 700; white-space: nowrap; }
.inspector-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #1e293b; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.inspector-table tr:hover { background: #f1f5f9; }

.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.8rem; }
.btn { padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0; background: white; cursor: pointer; font-weight: 600; }
.btn:hover:not(:disabled) { background: #f8fafc; border-color: #cbd5e1; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
