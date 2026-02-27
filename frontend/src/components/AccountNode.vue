<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ node: any; depth: number }>()
const emit = defineEmits(['view-ledger', 'view-info'])
const expanded = ref(props.node.level < 2)

function handleToggle() {
  if (props.node.children?.length > 0) expanded.value = !expanded.value
}
</script>

<template>
  <div class="node-wrapper">
    <!-- Row: left content (shrinks) | right actions (fixed 108px, never shrinks) -->
    <div class="node-row" :class="[`lvl-${node.level}`, { 'is-leaf': node.clv === 'S' }]"
         @click="handleToggle">

      <!-- Vertical guide line -->
      <div v-if="depth > 0" class="vline"
           :style="{ left: ((depth - 1) * 22 + 18) + 'px' }"></div>

      <!-- LEFT: indent + toggle + code + name (fills remaining space, clips overflow) -->
      <div class="n-left" :style="{ paddingLeft: (depth * 22 + 10) + 'px' }">
        <span v-if="node.children?.length" class="toggle" :class="{ open: expanded }">
          <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </span>
        <span v-else class="toggle-ph"></span>

        <span class="n-code">{{ node.code }}</span>
        <span class="n-name">{{ node.name }}</span>
      </div>

      <!-- RIGHT: always-visible action buttons — fixed 108px, flex-shrink:0 -->
      <div class="n-actions" @click.stop>
        <button class="ab ab-main" title="Ver Mayor" @click="emit('view-ledger', node)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v20M2 12h20"/>
          </svg>
          <span class="ab-txt">Mayor</span>
        </button>
        <button class="ab ab-info" title="Más Info" @click="emit('view-info', node)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span class="ab-txt">Info</span>
        </button>
      </div>
    </div>

    <!-- Children -->
    <div v-if="expanded && node.children">
      <AccountNode v-for="child in node.children" :key="child.id"
        :node="child" :depth="depth + 1"
        @view-ledger="n => emit('view-ledger', n)"
        @view-info="n => emit('view-info', n)"
      />
    </div>
  </div>
</template>

<style scoped>
/* ─ Row ──────────────────────────────────────────────────────── */
.node-row {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  position: relative;
  transition: background 0.14s;
  /* No min-width. No sticky. Pure flex. */
}
.node-row:hover { background: #f0f7ff !important; }

/* level colours */
.lvl-1 { background: #f1f5f9; border-left: 4px solid #2563eb; }
.lvl-1 .n-name { color: #1e3a8a; text-transform: uppercase; font-weight: 800; font-size: 0.9rem; }
.lvl-1 .n-code { color: #1d4ed8; font-weight: 700; }

.lvl-2 { background: #fff; }
.lvl-2 .n-name { color: #1e40af; font-weight: 700; }

.lvl-3 .n-name { color: #374151; font-weight: 600; font-size: 0.875rem; }
.lvl-4 .n-name, .lvl-5 .n-name { color: #4b5563; font-weight: 500; font-size: 0.85rem; }

/* guide line */
.vline {
  position: absolute; top: 0; bottom: 0;
  width: 1px; background: #e2e8f0; pointer-events: none;
}

/* ─ Left section ─────────────────────────────────────────────── */
.n-left {
  flex: 1 1 0;      /* fill all space left after actions */
  min-width: 0;     /* allow shrink */
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding-top: 0.65rem;
  padding-bottom: 0.65rem;
  padding-right: 0.25rem;
  overflow: hidden; /* clip overflowing name */
}

.toggle {
  flex-shrink: 0;
  width: 16px; height: 16px;
  display: flex; align-items: center; justify-content: center;
  color: #94a3b8;
  transition: transform 0.18s, color 0.18s;
}
.toggle.open { transform: rotate(90deg); color: #2563eb; }
.toggle-ph { flex-shrink: 0; width: 16px; }

.n-code {
  flex-shrink: 0;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 0.76rem;
  color: #64748b;
  white-space: nowrap;
}

.n-name {
  flex: 1 1 0;
  min-width: 0;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ─ RIGHT actions: FIXED WIDTH — never shrinks, always visible ─ */
.n-actions {
  flex-shrink: 0;  /* KEY: never gives up space */
  width: 108px;   /* fixed: just enough for 2 icon-text buttons */
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.3rem;
  padding: 0 0.5rem;
}

.ab {
  display: flex; align-items: center; gap: 0.25rem;
  padding: 0.28rem 0.5rem;
  border: none; border-radius: 6px;
  font-size: 0.68rem; font-weight: 600;
  cursor: pointer; font-family: inherit;
  transition: all 0.16s; white-space: nowrap;
}
.ab-main {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  box-shadow: 0 1px 4px rgba(37,99,235,.28);
}
.ab-main:hover { filter: brightness(1.1); transform: translateY(-1px); }

.ab-info { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
.ab-info:hover { background: #e0f2fe; color: #0369a1; transform: translateY(-1px); }

/* Hide button labels below 860px — icon only, shrink actions column */
@media (max-width: 860px) {
  .ab-txt { display: none; }
  .ab { padding: 0.32rem 0.38rem; }
  .n-actions { width: 68px; }
}
</style>
