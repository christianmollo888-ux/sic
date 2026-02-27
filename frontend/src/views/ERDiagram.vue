<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import mermaid from 'mermaid'

const diagramContainer = ref<HTMLElement | null>(null)

// Definición completa incluyendo todas las celdas y relaciones
const diagramDefinition = `
erDiagram
    accounts {
        int id PK
        string code UK
        string name
        string parent_code FK
    }
    journal_entries {
        int id PK
        string entry_code
        date date
    }
    entry_details {
        int id PK
        int entry_id FK
        int account_id FK
        numeric debit
        numeric credit
    }
    CN_TRANS {
        string MES
        string TIPO
        string NUMERO
        string COD_LCY FK
        string CODIGO FK
    }
    CN_PCTAS {
        string CODIGO PK
        string NOMBRE
    }
    CN_GLOSA {
        string MES
        string TIPO
        string NUMERO
        string GLOSA
    }
    CN_LCYLV {
        string COD_LCY PK
        string NOMBRE
    }

    journal_entries ||--o{ entry_details : "contiene"
    accounts ||--o{ entry_details : "vinculo"
    accounts ||--o{ accounts : "jerarquia"
    CN_PCTAS ||--o{ CN_TRANS : "ref_legacy"
    CN_GLOSA ||--o{ CN_TRANS : "cabecera"
    CN_LCYLV ||--o{ CN_TRANS : "soporte"
`

async function applyStyles() {
  await nextTick()
  if (!diagramContainer.value) return

  const svg = diagramContainer.value.querySelector('svg')
  if (!svg) {
    // Reintento breve si el DOM aún no está listo
    setTimeout(applyStyles, 100)
    return
  }

  // Buscamos TODOS los elementos de texto en el SVG
  const textElements = svg.querySelectorAll('text')
  
  textElements.forEach((textNode) => {
    const content = textNode.textContent?.trim() || ''
    
    // Identificamos las tablas legacy y modernas por su nombre exacto
    const isLegacy = content.startsWith('CN_')
    const isModern = ['accounts', 'journal_entries', 'entry_details'].includes(content)
    
    if (isLegacy || isModern) {
      // Subimos en el DOM hasta encontrar el grupo principal del nodo (<g class="node...">)
      let parent = textNode.parentElement
      while (parent && !(parent.tagName.toLowerCase() === 'g' && parent.classList.contains('node'))) {
        parent = parent.parentElement
      }
      
      if (parent) {
        // En Mermaid, el fondo principal de la tabla suele ser el primer <rect>
        // o los que tienen clase attributeBox / entityBox
        const rects = parent.querySelectorAll('rect')
        
        rects.forEach(rect => {
          if (isLegacy) {
            // Estilo Legacy: Gris con borde punteado
            rect.style.setProperty('fill', '#f8fafc', 'important')
            rect.style.setProperty('stroke', '#64748b', 'important')
            rect.style.setProperty('stroke-width', '2px', 'important')
            rect.style.setProperty('stroke-dasharray', '6,4', 'important')
          } else {
            // Estilo Moderno: Azul con borde sólido grueso
            rect.style.setProperty('fill', '#eff6ff', 'important')
            rect.style.setProperty('stroke', '#2563eb', 'important')
            rect.style.setProperty('stroke-width', '3px', 'important')
            // Asegurarse de quitar dasharray si lo tuviera por defecto
            rect.style.setProperty('stroke-dasharray', 'none', 'important')
          }
        })
      }
    }
  })
}

onMounted(async () => {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    er: {
      useMaxWidth: false,
      layoutDirection: 'LR', // Cambiado a Horizontal para mejor visibilidad de todas las tablas
      minEntityWidth: 180,
      minEntityHeight: 120
    },
    themeVariables: {
      primaryColor: '#ffffff',
      primaryTextColor: '#1e293b',
      lineColor: '#94a3b8',
      attributeBackgroundColor: '#ffffff',
      attributeFontColor: '#475569',
      fontSize: '14px'
    }
  })

  if (diagramContainer.value) {
    try {
      const { svg } = await mermaid.render('mermaid-diag', diagramDefinition)
      diagramContainer.value.innerHTML = svg
      // Aplicar estilos personalizados inmediatamente después del render
      await applyStyles()
    } catch (e) {
      console.error("Mermaid Render Error:", e)
      diagramContainer.value.innerHTML = "<p class='error'>Error al generar el diagrama dinámico.</p>"
    }
  }
})
</script>

<template>
  <div class="er-container">
    <div class="header-section">
      <h1>Diagrama Entidad-Relación</h1>
      <p class="text-muted">Visualización técnica completa de las 7 tablas (Legacy + Moderno).</p>
    </div>

    <div class="card diagram-card shadow-sm">
      <div ref="diagramContainer" class="mermaid-outer"></div>
    </div>
    
    <div class="card info-card">
      <h3>Diferenciación de Sistemas</h3>
      <div class="legend">
        <div class="legend-item">
          <div class="swatch modern"></div>
          <div>
            <strong>Sistema Moderno (Postgres)</strong>
            <p class="small text-muted">Borde Azul Sólido Grueso</p>
          </div>
        </div>
        <div class="legend-item">
          <div class="swatch legacy"></div>
          <div>
            <strong>Sistema Legacy (Histórico)</strong>
            <p class="small text-muted">Borde Gris Discontinuo</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.er-container { padding: 1rem 0 4rem; }
.header-section { margin-bottom: 2.5rem; }

.diagram-card { 
  display: block; padding: 2rem; background: #fafafa; border-radius: 20px; 
  min-height: 700px; overflow-x: auto; border: 1px solid #e5e7eb;
}
.mermaid-outer { min-width: 1200px; display: flex; justify-content: center; }

.info-card { margin-top: 2rem; padding: 2rem; border-radius: 16px; }
.legend { display: flex; gap: 4rem; margin-top: 1.5rem; }
.legend-item { display: flex; align-items: flex-start; gap: 1rem; }
.swatch { width: 48px; height: 28px; border-radius: 6px; border: 3px solid; flex-shrink: 0; }
.modern { background: #eff6ff; border-color: #2563eb; }
.legacy { background: #f8fafc; border-color: #64748b; border-style: dashed; }

.small { font-size: 0.85rem; margin: 0; }
.error { color: #dc2626; background: #fee2e2; padding: 1.5rem; border-radius: 12px; text-align: center; }

/* Mermaid Custom Fixes */
:deep(.entityLabel) { font-weight: 900 !important; font-size: 15px !important; text-transform: uppercase; }
:deep(.relationshipLabelRect) { fill: #ffffff !important; opacity: 0.9; }
:deep(.relationshipLabel) { font-weight: 700 !important; fill: #1e293b !important; }
</style>
