const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export type ChartPayload = {
  type: string
  title: string
  labels: string[]
  values: number[]
}

export type AnalysisResponse = {
  chat_id: number
  question: string
  answer: string
  sql: string
  columns: string[]
  rows: Record<string, string | number>[]
  chart: ChartPayload | null
  insights: string[]
}

export type DatasetInfo = {
  id: number
  name: string
  source: string
  table_name: string
  description: string
  columns: string[]
}

export type MetricCard = {
  label: string
  value: string | number
  helper: string
}

export type SeriesPoint = {
  label: string
  value: number
}

export type OverviewResponse = {
  metrics: MetricCard[]
  monthly_revenue: SeriesPoint[]
  revenue_by_region: SeriesPoint[]
  revenue_by_category: SeriesPoint[]
  top_products: SeriesPoint[]
}

export type AlertInfo = {
  id: number
  title: string
  metric: string
  operator: string
  threshold: number
  current_value: number
  severity: string
  status: string
}

export type ReportInfo = {
  id: number
  title: string
  period: string
  summary: string
  payload: OverviewResponse
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('brainwave_token')
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erro inesperado' }))
    throw new Error(error.detail || 'Erro inesperado')
  }
  return response.json()
}

export async function loginDemo() {
  const data = await request<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email: 'analyst@brainwave.bi', password: 'analyst123' }),
  })
  localStorage.setItem('brainwave_token', data.access_token)
  return data
}

export function askQuestion(question: string, chatId?: number | null) {
  return request<AnalysisResponse>('/chat/ask', {
    method: 'POST',
    body: JSON.stringify({ question, chat_id: chatId }),
  })
}

export function listDatasets() {
  return request<DatasetInfo[]>('/datasets')
}

export function getSalesSample() {
  return request<Record<string, string | number>[]>('/datasets/sales/sample')
}

export function uploadSalesCsv(file: File, replace = true) {
  const formData = new FormData()
  formData.append('file', file)
  return request<{ imported_rows: number; replace: boolean }>(`/datasets/sales/upload?replace=${replace}`, {
    method: 'POST',
    body: formData,
  })
}

export function getOverview() {
  return request<OverviewResponse>('/analytics/overview')
}

export function listAlerts() {
  return request<AlertInfo[]>('/alerts')
}

export function listReports() {
  return request<ReportInfo[]>('/reports')
}

export function createReport(title = 'Resumo executivo', period = '2026-H1') {
  return request<ReportInfo>('/reports', {
    method: 'POST',
    body: JSON.stringify({ title, period }),
  })
}

export function exportUrl() {
  return `${API_URL}/datasets/sales/export`
}
