<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { systemService } from '../services/api'

const metadata = ref<Record<string, any>>({})
const relationships = ref<any[]>([])
const loading = ref(true)
const selectedTable = ref('')

onMounted(async () => {
  try {
    const res = await systemService.getSchema()
    metadata.value = res.data.metadata
    relationships.value = res.data.relationships
    
    const tableNames = Object.keys(metadata.value)
    if (tableNames.length > 0) {
      selectedTable.value = tableNames[0]
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// Computes relevant relationships based on selected table
const relevantRelationships = computed(() => {
  if (!selectedTable.value || !relationships.value) return []
  return relationships.value.filter(rel => 
    rel.from.includes(selectedTable.value) || rel.to.includes(selectedTable.value)
  )
})
</script>

<template>
  <div>
    <div class="header-section">
      <h1>Diccionario de Datos</h1>
      <p class="text-muted">Documentación técnica de la estructura de base de datos y sus vínculos.</p>
    </div>

    <div v-if="loading" class="card">Cargando metadatos del esquema...</div>
    
    <div v-else class="dictionary-layout">
      <!-- Sidebar Tables -->
      <div class="sidebar card">
        <h3>Tablas</h3>
        <ul class="table-list">
          <li 
            v-for="(_, table) in metadata" 
            :key="table" 
            @click="selectedTable = String(table)"
            :class="{ active: selectedTable === table }"
          >
            {{ table }}
            <span class="badge-mini" :class="String(table).startsWith('CN_') ? 'legacy' : 'modern'">
              {{ String(table).startsWith('CN_') ? 'L' : 'M' }}
            </span>
          </li>
        </ul>
      </div>

      <!-- Content Area -->
      <div class="content-area">
        <!-- Schema Card -->
        <div v-if="selectedTable" class="card">
          <div class="card-header-flex">
             <h3>Definición: {{ selectedTable }}</h3>
             <span class="type-tag">{{ selectedTable.startsWith('CN_') ? 'Tabla Legacy' : 'Tabla Moderna' }}</span>
          </div>
          
          <p class="table-description tech-text">{{ metadata[selectedTable]?.description }}</p>

          <table class="metadata-table">
            <thead>
              <tr>
                <th>Columna</th>
                <th>Tipo</th>
                <th>Nulable</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="col in metadata[selectedTable]?.columns" :key="col.column">
                <td class="mono">{{ col.column }}</td>
                <td><code class="type-code">{{ col.type }}</code></td>
                <td>{{ col.nullable ? 'Sí' : 'No' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Sample Data Card -->
        <div v-if="selectedTable && metadata[selectedTable]?.sample_data?.length > 0" class="card">
          <h3>Ejemplos de Datos</h3>
          <p class="text-muted small">Muestra rápida de registros existentes (hasta 3 filas).</p>
          
          <div class="table-container mt-2">
            <table class="metadata-table sample-table">
              <thead>
                <tr>
                  <th v-for="(v, k) in metadata[selectedTable].sample_data[0]" :key="'th-'+k">{{ k }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in metadata[selectedTable].sample_data" :key="'row-'+idx">
                   <td v-for="(v, k) in row" :key="'td-'+k+'-'+idx" class="mono small-text">{{ v === null ? 'NULL' : v }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div v-if="selectedTable && metadata[selectedTable]?.sample_data?.length === 0" class="card bg-warning-light">
          <p class="text-warning text-center m-0">No se encontraron datos de ejemplo en esta tabla.</p>
        </div>

        <!-- Relationships Card -->
        <div class="card relationship-card">
          <h3>Relaciones de la Tabla</h3>
          <p class="text-muted small">Vínculos detectados que involucran a <strong>{{ selectedTable }}</strong>.</p>
          
          <div v-if="relevantRelationships.length === 0" class="empty-state mt-2">
             No hay relaciones documentadas para esta tabla.
          </div>
          
          <div v-else class="relationship-list">
            <div v-for="(rel, idx) in relevantRelationships" :key="idx" class="rel-item-container">
              <div class="rel-item">
                 <div class="rel-node from">{{ rel.from }}</div>
                 <div class="rel-arrow">
                   <span class="rel-type">{{ rel.type }}</span>
                   <div class="arrow"></div>
                 </div>
                 <div class="rel-node to">{{ rel.to }}</div>
              </div>
              <p class="rel-description tech-text mt-2 mb-0">{{ rel.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { margin-bottom: 2rem; }
.dictionary-layout { display: grid; grid-template-columns: 280px 1fr; gap: 1.5rem; align-items: start; }

.sidebar { padding: 1.5rem; position: sticky; top: 100px; }
.table-list { list-style: none; padding: 0; margin-top: 1rem; }
.table-list li { 
  padding: 0.75rem 1rem; border-radius: 8px; cursor: pointer; 
  display: flex; justify-content: space-between; align-items: center;
  font-weight: 600; color: #475569; transition: all 0.2s;
  border: 1px solid transparent;
}
.table-list li:hover { background: #f1f5f9; color: #2563eb; }
.table-list li.active { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }

.badge-mini { font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
.legacy { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.modern { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }

.content-area { display: flex; flex-direction: column; gap: 1.5rem; }
.card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.type-tag { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; background: #f1f5f9; padding: 4px 10px; border-radius: 20px; }

.table-description {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
  border-radius: 4px;
}

.tech-text {
  font-size: 0.9rem;
  line-height: 1.5;
  color: #334155;
}

.table-container {
  overflow-x: auto;
}

.metadata-table { width: 100%; border-collapse: collapse; }
.metadata-table th { text-align: left; padding: 0.75rem; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.8rem; text-transform: uppercase; white-space: nowrap; }
.metadata-table td { padding: 0.75rem; border-bottom: 1px solid #f1f5f9; }

.sample-table td { white-space: nowrap; max-width: 250px; overflow: hidden; text-overflow: ellipsis; }

.type-code { background: #f8fafc; padding: 2px 6px; border-radius: 4px; border: 1px solid #e2e8f0; font-size: 0.85rem; color: #ef4444; }

.relationship-card h3 { margin-bottom: 0.25rem; }
.relationship-list { margin-top: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }

.rel-item-container {
  background: #f8fafc; 
  padding: 1rem; 
  border-radius: 12px; 
  border: 1px solid #e2e8f0;
}

.rel-item { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.rel-node { font-family: monospace; font-weight: 700; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; text-align: center; }
.from { background: #2563eb; color: white; min-width: 150px; }
.to { background: #10b981; color: white; min-width: 150px; }

.rel-arrow { flex-grow: 1; display: flex; flex-direction: column; align-items: center; position: relative; min-width: 100px; }
.rel-type { font-size: 0.7rem; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 4px; text-align: center; }
.arrow { height: 2px; background: #cbd5e1; width: 100%; position: relative; }
.arrow::after { content: ''; position: absolute; right: -5px; top: -4px; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid #cbd5e1; }

.rel-description {
  padding-top: 0.75rem;
  border-top: 1px dashed #cbd5e1;
}

.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.85rem; font-weight: 600; }
.small { font-size: 0.85rem; }
.small-text { font-size: 0.75rem; }
.mt-2 { margin-top: 0.5rem; }
.mb-0 { margin-bottom: 0; }
.m-0 { margin: 0; }

.bg-warning-light { background-color: #fffbeb; border: 1px solid #fde68a; }
.text-warning { color: #d97706; }
.text-center { text-align: center; }
.empty-state { padding: 1.5rem; background: #f8fafc; border-radius: 8px; text-align: center; color: #64748b; font-style: italic; }
</style>
