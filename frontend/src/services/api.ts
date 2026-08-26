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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('brainwave_token')
  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
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

export function exportUrl() {
  return `${API_URL}/datasets/sales/export`
}
