import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export const accountService = {
  getAll: (skip = 0, limit = 100) => api.get(`/accounts/?skip=${skip}&limit=${limit}`),
  getLedger: (id: number) => api.get(`/accounts/${id}/ledger/`)
}

export const entryService = {
  getAll: (skip = 0, limit = 100) => api.get(`/entries/?skip=${skip}&limit=${limit}`),
  create: (data: any) => api.post('/entries/', data),
  getComprobantePdf: (id: number) => api.get(`/reports/comprobante/${id}`, { responseType: 'blob' })
}

export const systemService = {
  getTables: () => api.get('/system/tables'),
  getTableData: (tableName: string, skip = 0, limit = 100) => api.get(`/system/tables/${tableName}/data?skip=${skip}&limit=${limit}`),
  getCapacityStats: () => api.get('/system/stats/capacity'),
  getTotalsComparison: () => api.get('/system/stats/totals'),
  getSchema: () => api.get('/system/schema')
}
