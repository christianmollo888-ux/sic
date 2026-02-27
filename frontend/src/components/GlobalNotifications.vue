<script setup lang="ts">
import { useNotifications } from '../composables/useNotifications'

const { toasts, removeToast, confirmState, handleConfirm } = useNotifications()
</script>

<template>
  <div class="notifications-wrapper">
    <!-- Toasts Container -->
    <div class="toast-container">
      <transition-group name="toast">
        <div 
          v-for="toast in toasts" 
          :key="toast.id" 
          :class="['toast-item', `toast-${toast.type}`]"
          @click="removeToast(toast.id)"
        >
          <div class="toast-icon">
            <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          </div>
          <div class="toast-message">{{ toast.message }}</div>
          <button class="toast-close">&times;</button>
        </div>
      </transition-group>
    </div>

    <!-- Global Confirm Dialog -->
    <transition name="modal">
      <div v-if="confirmState.show" class="confirm-backdrop" @click.self="handleConfirm(false)">
        <div class="confirm-card">
          <div class="confirm-header" :class="{ 'is-danger': confirmState.danger }">
            <div class="confirm-icon">
              <svg v-if="confirmState.danger" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </div>
            <h3>{{ confirmState.title }}</h3>
          </div>
          <div class="confirm-body">
            <p>{{ confirmState.message }}</p>
          </div>
          <div class="confirm-footer">
            <button class="btn-cancel" @click="handleConfirm(false)">{{ confirmState.cancelText }}</button>
            <button 
              :class="['btn-confirm', { 'danger': confirmState.danger }]" 
              @click="handleConfirm(true)"
            >
              {{ confirmState.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.notifications-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 0; /* Don't block clicks */
  z-index: 10000;
}

/* Toasts */
.toast-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 10001;
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  min-width: 300px;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 4px solid #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
}

.toast-item:hover { transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

.toast-success { border-left-color: #10b981; }
.toast-error { border-left-color: #ef4444; }
.toast-info { border-left-color: #3b82f6; }
.toast-warning { border-left-color: #f59e0b; }

.toast-icon { flex-shrink: 0; }
.toast-success .toast-icon { color: #10b981; }
.toast-error .toast-icon { color: #ef4444; }
.toast-info .toast-icon { color: #3b82f6; }
.toast-warning .toast-icon { color: #f59e0b; }

.toast-message { flex: 1; font-size: 0.9rem; font-weight: 500; color: #1e293b; }
.toast-close { background: none; border: none; font-size: 1.25rem; color: #94a3b8; cursor: pointer; padding: 0.25rem; line-height: 1; border-radius: 4px; }
.toast-close:hover { background: #f1f5f9; color: #1e293b; }

/* Modal Confirm */
.confirm-backdrop {
  height: 100vh;
  width: 100vw;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  pointer-events: auto;
}

.confirm-card {
  background: white;
  width: 100%;
  max-width: 440px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: cardIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardIn {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.confirm-header {
  padding: 1.5rem 1.5rem 0.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.confirm-icon {
  width: 56px;
  height: 56px;
  border-radius: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  color: #3b82f6;
}

.is-danger .confirm-icon {
  background: #fef2f2;
  color: #ef4444;
}

.confirm-header h3 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: #1e293b;
}

.confirm-body {
  padding: 0.5rem 2rem 1.5rem 2rem;
  text-align: center;
  color: #64748b;
  font-size: 1rem;
  line-height: 1.6;
}

.confirm-footer {
  padding: 1.5rem;
  background: #f8fafc;
  display: flex;
  gap: 1rem;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 0.875rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-cancel {
  background: white;
  border-color: #e2e8f0;
  color: #64748b;
}

.btn-cancel:hover { background: #f1f5f9; color: #1e293b; border-color: #cbd5e1; }

.btn-confirm {
  background: #3b82f6;
  color: white;
}

.btn-confirm:hover { background: #2563eb; transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); }

.btn-confirm.danger {
  background: #ef4444;
}

.btn-confirm.danger:hover { background: #dc2626; box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2); }

/* Transitions */
.toast-enter-active, .toast-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: scale(0.9); }

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
