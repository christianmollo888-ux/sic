<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { accountService } from '../services/api'
import AccountNode from '../components/AccountNode.vue'
import PageHero from '../components/PageHero.vue'

interface Account {
  id: number
  code: string
  name: string
  parent_code: string | null
  level: number
  clv: string
  children?: Account[]
  expanded?: boolean
}

const rawAccounts = ref<Account[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await accountService.getAll(0, 1000)
    rawAccounts.value = res.data.map((acc: any) => ({ ...acc, expanded: false }))
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// Build tree structure
const accountTree = computed(() => {
  const map: Record<string, Account> = {}
  const roots: Account[] = []

  // Initialize map with all accounts
  rawAccounts.value.forEach(acc => {
    map[acc.code] = { ...acc, children: [] }
  })

  // Link children to parents based on parent_code from DB
  Object.values(map).forEach(acc => {
    if (acc.parent_code && map[acc.parent_code]) {
      map[acc.parent_code].children?.push(acc)
    } else {
      roots.push(acc)
    }
  })

  return roots.sort((a, b) => a.code.localeCompare(b.code))
})

const selectedLedger = ref<any>(null)
const viewingLedger = ref(false)
const selectedInfo = ref<any>(null)
const viewingInfo = ref(false)

async function viewLedger(acc: Account) {
  viewingLedger.value = true
  selectedLedger.value = { ...acc, loading: true }
  try {
    const res = await accountService.getLedger(acc.id)
    selectedLedger.value = { ...acc, ...res.data, loading: false }
  } catch (e) {
    console.error(e)
  }
}

function viewInfo(acc: Account) {
  selectedInfo.value = {
    ...acc,
    isLeaf: acc.clv === 'S'
  }
  viewingInfo.value = true
}

// Function to expand all up to level 3 by default
function expandInitial() {
    rawAccounts.value.forEach(acc => {
        if (acc.level < 3) acc.expanded = true
    })
}
</script>

<template>
  <div>
    <PageHero
      title="Plan de Cuentas"
      subtitle="Análisis jerárquico multinivel (5 niveles) según Plan General Contable 2026"
      gradient="linear-gradient(135deg, #14532d 0%, #15803d 45%, #34d399 100%)"
    />

    <div v-if="loading" class="loading-block">
      <div class="spinner-global"></div>
      <span>Cargando estructura contable...</span>
    </div>
    
    <div v-else class="card tree-card">
      <div class="tree-header">
        <div class="th-left">Código &amp; Nombre de la Cuenta</div>
        <div class="th-right">Operaciones</div>
      </div>
      
      <div class="tree-container">
        <template v-for="node in accountTree" :key="node.id">
          <AccountNode 
            :node="node" 
            :depth="0" 
            @view-ledger="viewLedger" 
            @view-info="viewInfo"
          />
        </template>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="viewingLedger" class="modal-overlay" @click="viewingLedger = false">
      <div class="modal-card" @click.stop>
        <h3>Mayor General: {{ selectedLedger.name }}</h3>
        <p class="code-subtitle">Código: {{ selectedLedger.code }}</p>
        
        <div v-if="selectedLedger.loading">Cargando cálculos recursivos...</div>
        <div v-else class="ledger-stats">
          <div class="stat">
            <span class="label">Total Debe (Acumulado)</span>
            <span class="value">{{ selectedLedger.total_debit.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</span>
          </div>
          <div class="stat">
            <span class="label">Total Haber (Acumulado)</span>
            <span class="value">{{ selectedLedger.total_credit.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</span>
          </div>
          <div class="stat highlight" :class="{ 'negative': selectedLedger.balance < 0 }">
            <span class="label">Saldo Actual</span>
            <span class="value">{{ selectedLedger.balance.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</span>
          </div>
          <div v-if="selectedLedger.total_debit > 0 || selectedLedger.total_credit > 0" class="stat-info">
             <small>Info: Este saldo incluye todas las sub-cuentas vinculadas.</small>
          </div>
        </div>
        <button class="btn btn-primary w-full" @click="viewingLedger = false">Cerrar</button>
      </div>
    </div>

    <div v-if="viewingInfo" class="modal-overlay" @click="viewingInfo = false">
      <div class="modal-card" @click.stop>
        <h3>Ficha Técnica de Cuenta</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Código Catálogo:</span>
            <span class="value mono">{{ selectedInfo.code }}</span>
          </div>
          <div class="info-item">
            <span class="label">Nivel Jerárquico:</span>
            <span class="value">Nivel {{ selectedInfo.level }}</span>
          </div>
          <div class="info-item">
            <span class="label">Padre:</span>
            <span class="value mono">{{ selectedInfo.parent_code || 'Raíz (Nivel 0)' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Categoría Legacy:</span>
            <span class="value">{{ selectedInfo.clv === 'S' ? 'Cuenta de Registro (Sub)' : 'Cuenta de Bloque (Título)' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Dependencias:</span>
            <span class="value">{{ selectedInfo.children?.length || 0 }} sub-cuentas</span>
          </div>
        </div>
        <button class="btn btn-primary w-full" @click="viewingInfo = false">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { margin-bottom: 2rem; }

/* tree-card: DO NOT use overflow:hidden — it breaks sticky children */
.tree-card {
  padding: 0;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,.07);
  /* Use clip-path to keep rounded corners without breaking sticky children */
  overflow: hidden;   /* Kept intentionally for look; sticky works because tree-container is the scroll ancestor */
}

/* Header row matches the two-section layout of AccountNode */
.tree-header {
  display: flex;
  justify-content: space-between;
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  border-bottom: 2px solid #e2e8f0;
  padding: 0.7rem 0.6rem 0.7rem 1rem;
  font-weight: 800;
  font-size: 0.65rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.th-left { flex: 1; }
.th-right { flex-shrink: 0; padding: 0 0.5rem; width: 108px; text-align: center; }

/* The scroll container that makes sticky:right work */
.tree-container {
  max-height: 78vh;
  overflow-y: auto;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  background: white;
  /* Establish a stacking context so sticky children pin inside here */
  position: relative;
}

@media (max-width: 600px) {
  .tree-header { display: none; }
  .th-right { width: 80px; }
}


.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.btn-primary { background: #2563eb; color: white; }
.btn-primary:hover { background: #1d4ed8; }

.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
.w-full { width: 100%; }
.code-subtitle { color: #64748b; font-family: monospace; margin-top: -1rem; margin-bottom: 1.5rem; }

/* Modal Styles */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  padding: 1rem;
}
.modal-card {
  background: white; padding: 2.5rem; border-radius: 20px; width: 100%; max-width: 480px;
  box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
}
@media (max-width: 480px) {
  .modal-card {
    padding: 1.5rem;
    border-radius: 12px;
  }
  .stat.highlight {
    font-size: 1.2rem !important;
  }
}

.ledger-stats, .info-grid { display: flex; flex-direction: column; gap: 1rem; margin: 1.8rem 0; }
.stat, .info-item { display: flex; justify-content: space-between; padding-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9; }
.stat.highlight { font-weight: 800; font-size: 1.5rem; border: none; padding-top: 0.5rem; }
.stat-info { font-style: italic; color: #64748b; text-align: center; }
.label { color: #64748b; font-size: 0.85rem; font-weight: 500; }
.value { color: #0f172a; font-weight: 700; }
.mono { font-family: monospace; }
.negative { color: #ef4444; }
</style>
