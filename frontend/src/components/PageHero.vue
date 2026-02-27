<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  gradient?: string
}>()
</script>

<template>
  <header class="page-hero" :style="gradient ? `background: ${gradient}` : ''">
    <div class="hero-content">
      <h1>{{ title }}</h1>
      <p v-if="subtitle" class="hero-subtitle">{{ subtitle }}</p>
    </div>
    <slot />
  </header>
</template>

<style scoped>
.page-hero {
  background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 45%, #0ea5e9 100%);
  border-radius: 16px;
  padding: 2rem 2.5rem;
  margin-bottom: 1.75rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(30, 58, 138, .4);
}

/* Decorative circles */
.page-hero::before,
.page-hero::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  pointer-events: none;
}
.page-hero::before {
  width: 280px; height: 280px;
  background: white;
  top: -80px; right: -50px;
}
.page-hero::after {
  width: 140px; height: 140px;
  background: white;
  bottom: -50px; right: 150px;
}

.hero-content {
  position: relative;
  z-index: 1;
}

h1 {
  font-size: 1.9rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 0.3rem 0;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.hero-subtitle {
  color: rgba(255,255,255,.75);
  font-size: 0.95rem;
  margin: 0;
}

@media (max-width: 600px) {
  .page-hero { padding: 1.4rem 1.25rem; }
  h1 { font-size: 1.4rem; }
}
</style>
