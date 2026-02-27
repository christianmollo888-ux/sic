<script setup lang="ts">
import { ref } from 'vue'
import GlobalNotifications from './components/GlobalNotifications.vue'
import AppFooter from './components/AppFooter.vue'

const menuOpen = ref(false)
const toggleMenu = () => { menuOpen.value = !menuOpen.value }
const closeMenu = () => { menuOpen.value = false }
</script>

<template>
  <GlobalNotifications />
  <nav class="navbar">
    <div class="nav-content">
      <span class="logo">SIC4BUS</span>

      <!-- Hamburger button (mobile only) -->
      <button class="hamburger" @click="toggleMenu" :aria-expanded="menuOpen" aria-label="Abrir menú">
        <span class="bar" :class="{ open: menuOpen }"></span>
        <span class="bar" :class="{ open: menuOpen }"></span>
        <span class="bar" :class="{ open: menuOpen }"></span>
      </button>

      <!-- Backdrop for mobile -->
      <div class="nav-backdrop" v-if="menuOpen" @click="closeMenu"></div>

      <div class="nav-links" :class="{ 'nav-open': menuOpen }">
        
        <!-- Grupo Contabilidad -->
        <div class="nav-item">
          <button class="nav-button">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Contabilidad
            <svg class="chevron-down" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>
          <div class="dropdown-menu">
            <router-link to="/" @click="closeMenu">Plan de Cuentas</router-link>
            <router-link to="/entries" @click="closeMenu">Asientos</router-link>
            <router-link to="/reports" @click="closeMenu">Reportes</router-link>
          </div>
        </div>

        <!-- Grupo Formularios de Certificación SIAT -->
        <div class="nav-item">
          <button class="nav-button">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            Formularios SIAT
            <svg class="chevron-down" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>
          <div class="dropdown-menu">
            <router-link to="/forms" @click="closeMenu">Procesar Formulario</router-link>
            <router-link to="/form-history" @click="closeMenu">Historial</router-link>
            <router-link to="/tax-audit" @click="closeMenu">Auditoría Tributaria</router-link>
            <router-link to="/resumen-200" @click="closeMenu">Resumen Formulario 200</router-link>
          </div>
        </div>

        <!-- Grupo Gestión de información -->
        <div class="nav-item">
          <button class="nav-button">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
            Gestión
            <svg class="chevron-down" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>
          <div class="dropdown-menu">
            <router-link to="/inspector" @click="closeMenu">Inspector de Datos</router-link>
            <router-link to="/statistics" @click="closeMenu">Estadísticas</router-link>
            <router-link to="/dictionary" @click="closeMenu">Diccionario</router-link>
            <router-link to="/diagram" @click="closeMenu">Diagrama ER</router-link>
          </div>
        </div>

      </div>
    </div>
  </nav>
  
  <main class="container">
    <router-view></router-view>
  </main>
  <AppFooter />
</template>

<style scoped>
/* Ensure app stretches full height for footer positioning */
:global(#app) {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

:global(.container) {
  flex: 1;
}

.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  padding: 0.875rem 2rem;
  position: sticky;
  top: 0;
  z-index: 200;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: background 0.3s ease;
}

@media (max-width: 768px) {
  .navbar {
    padding: 0.75rem 1rem;
  }
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.logo {
  font-weight: 800;
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--primary) 0%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
  z-index: 201;
}

/* ── Hamburger ─────────────────────────────────── */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 28px;
  height: 20px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 201;
}

.bar {
  display: block;
  width: 100%;
  height: 2.5px;
  background: var(--text);
  border-radius: 9999px;
  transition: transform 0.3s ease, opacity 0.3s ease;
  transform-origin: center;
}

/* Animate to X */
.hamburger .bar:nth-child(1).open { transform: translateY(8.75px) rotate(45deg); }
.hamburger .bar:nth-child(2).open { opacity: 0; transform: scaleX(0); }
.hamburger .bar:nth-child(3).open { transform: translateY(-8.75px) rotate(-45deg); }

@media (max-width: 900px) {
  .hamburger {
    display: flex;
  }
}

/* ── Nav backdrop (mobile) ──────────────────────── */
.nav-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(2px);
  z-index: 199;
}

/* ── Nav links ─────────────────────────────────── */
.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

@media (max-width: 900px) {
  .nav-links {
    display: none;
    position: fixed;
    top: 0;
    right: 0;
    width: min(300px, 85vw);
    height: 100vh;
    background: white;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    padding: 5rem 1rem 2rem;
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
    overflow-y: auto;
    z-index: 200;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .nav-links.nav-open {
    display: flex;
  }
}

/* ── Nav item ──────────────────────────────────── */
.nav-item {
  position: relative;
}

@media (max-width: 900px) {
  .nav-item {
    width: 100%;
  }
}

.nav-button {
  background: transparent;
  border: none;
  font-family: inherit;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  width: 100%;
}

.nav-button:hover,
.nav-item:hover .nav-button {
  background: rgba(37, 99, 235, 0.08);
  color: var(--primary);
}

.nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: color 0.2s ease;
  flex-shrink: 0;
}

.chevron-down {
  width: 1rem;
  height: 1rem;
  transition: transform 0.3s ease;
  margin-left: auto;
}

.nav-item:hover .chevron-down {
  transform: rotate(180deg);
}

/* ── Dropdown ──────────────────────────────────── */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  background: white;
  min-width: 220px;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border);
  padding: 0.5rem;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  z-index: -1;
}

.nav-item:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  z-index: 50;
}

/* Invisible bridge so mouse hover doesn't drop off */
.nav-item::after {
  content: '';
  position: absolute;
  height: 1.5rem;
  width: 100%;
  bottom: -1.5rem;
  left: 0;
}

@media (max-width: 900px) {
  /* On mobile: dropdown renders inline (no absolute positioning) */
  .dropdown-menu {
    position: static;
    opacity: 1;
    visibility: visible;
    transform: none;
    box-shadow: none;
    border: none;
    border-left: 2px solid var(--border);
    border-radius: 0;
    padding: 0.25rem 0.5rem;
    background: transparent;
    margin-left: 1rem;
    z-index: auto;
  }

  .nav-item::after {
    display: none;
  }
}

.dropdown-menu a {
  text-decoration: none;
  color: var(--text);
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.625rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: block;
}

.dropdown-menu a:hover {
  background: var(--bg);
  color: var(--primary);
  transform: translateX(4px);
}

.dropdown-menu a.router-link-active {
  background: rgba(37, 99, 235, 0.08);
  color: var(--primary);
  font-weight: 600;
}

@media (max-width: 900px) {
  .dropdown-menu a:hover {
    transform: none;
  }
}
</style>
