import { ref, reactive } from 'vue'

export type NotificationType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: number
  message: string
  type: NotificationType
  duration?: number
}

export interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

const toasts = ref<Toast[]>([])
const confirmState = reactive({
  show: false,
  title: '',
  message: '',
  confirmText: 'Aceptar',
  cancelText: 'Cancelar',
  danger: false,
  resolve: null as ((val: boolean) => void) | null
})

let nextId = 0

export function useNotifications() {
  const notify = (message: string, type: NotificationType = 'info', duration = 5000) => {
    const id = nextId++
    const toast: Toast = { id, message, type, duration }
    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    return id
  }

  const removeToast = (id: number) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      confirmState.title = options.title
      confirmState.message = options.message
      confirmState.confirmText = options.confirmText || 'Aceptar'
      confirmState.cancelText = options.cancelText || 'Cancelar'
      confirmState.danger = options.danger || false
      confirmState.resolve = resolve
      confirmState.show = true
    })
  }

  const handleConfirm = (value: boolean) => {
    if (confirmState.resolve) {
      confirmState.resolve(value)
    }
    confirmState.show = false
  }

  return {
    toasts,
    confirmState,
    notify,
    removeToast,
    confirm,
    handleConfirm
  }
}
