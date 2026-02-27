<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loadTime = ref<number | null>(null)
const pageSize = ref<string>('-')
const userAgent = ref<string>('-')

onMounted(() => {
  // Calculate load time using Performance API
  const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined
  if (navEntry) {
    loadTime.value = Math.round(navEntry.loadEventEnd - navEntry.startTime)
  } else {
    // Fallback: measure from mount
    loadTime.value = Math.round(performance.now())
  }

  // Approximate page size from DOM
  const htmlBytes = document.documentElement.innerHTML.length
  const kb = htmlBytes / 1024
  pageSize.value = kb < 1024 ? `${kb.toFixed(1)} KB` : `${(kb / 1024).toFixed(2)} MB`

  // Simplified browser info
  const ua = navigator.userAgent
  if (ua.includes('Chrome')) userAgent.value = 'Chrome'
  else if (ua.includes('Firefox')) userAgent.value = 'Firefox'
  else if (ua.includes('Safari')) userAgent.value = 'Safari'
  else if (ua.includes('Edge')) userAgent.value = 'Edge'
  else userAgent.value = 'Desconocido'
})

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <!-- Stats Row -->
      <div class="footer-stats">
        <div class="stat-chip">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span>Carga: <strong>{{ loadTime !== null ? `${loadTime} ms` : '...' }}</strong></span>
        </div>
        <div class="stat-chip">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span>Peso DOM: <strong>{{ pageSize }}</strong></span>
        </div>
        <div class="stat-chip">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12" y2="18"/></svg>
          <span>Navegador: <strong>{{ userAgent }}</strong></span>
        </div>
        <div class="stat-chip">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
          <span>Versión: <strong>v2.0.0</strong></span>
        </div>
      </div>

      <!-- Copyright / Brand -->
      <div class="footer-copy">
        <span class="copy-symbol">&copy;</span>
        <span>{{ currentYear }}</span>
        <span class="dot">&bull;</span>
        <span>Desarrollado por: <strong>Christian Mollo</strong> para <strong class="brand">FORBUS S.R.L.</strong></span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #94a3b8;
  font-size: 0.78rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 0.85rem 2rem;
  margin-top: auto;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* Stats */
.footer-stats {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 0.25rem 0.625rem;
  color: #94a3b8;
  transition: background 0.2s;
}

.stat-chip:hover {
  background: rgba(255, 255, 255, 0.1);
}

.stat-chip svg {
  color: #60a5fa;
  flex-shrink: 0;
}

.stat-chip strong {
  color: #e2e8f0;
  font-weight: 600;
}

/* Copyright */
.footer-copy {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}

.copy-symbol {
  color: #60a5fa;
  font-weight: 700;
}

.dot {
  color: #475569;
  margin: 0 0.15rem;
}

.footer-copy strong {
  color: #cbd5e1;
}

.brand {
  color: #60a5fa !important;
  font-weight: 700;
}
</style>
