<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  askQuestion,
  createReport,
  exportUrl,
  getOverview,
  getSalesSample,
  listDatasets,
  listAlerts,
  listReports,
  loginDemo,
  uploadSalesCsv,
  type AlertInfo,
  type AnalysisResponse,
  type ChartPayload,
  type DatasetInfo,
  type OverviewResponse,
  type ReportInfo,
} from '../services/api'

type ChatMessage = {
  id: number
  role: 'ai' | 'user'
  text: string
  analysis?: AnalysisResponse
}

const question = ref('Qual produto vendeu mais?')
const isTyping = ref(false)
const error = ref('')
const chatId = ref<number | null>(null)
const datasets = ref<DatasetInfo[]>([])
const sampleRows = ref<Record<string, string | number>[]>([])
const overview = ref<OverviewResponse | null>(null)
const alerts = ref<AlertInfo[]>([])
const reports = ref<ReportInfo[]>([])
const uploadStatus = ref('')
const isUploading = ref(false)

const chatHistory = ref<ChatMessage[]>([
  {
    id: 1,
    role: 'ai',
    text: 'Ola! Eu analiso o dataset de vendas e devolvo SQL seguro, tabela, grafico e insights.',
  },
])

const latestAnalysis = computed(() => {
  return [...chatHistory.value].reverse().find((msg) => msg.analysis)?.analysis
})

const dashboardMetrics = computed(() => {
  if (overview.value?.metrics.length) return overview.value.metrics
  return [
    { label: 'Receita total', value: '--', helper: 'Aguardando API' },
    { label: 'Pedidos', value: '--', helper: 'Aguardando API' },
    { label: 'Ticket medio', value: '--', helper: 'Aguardando API' },
    { label: 'Regiao lider', value: '--', helper: 'Aguardando API' },
  ]
})

const totalRevenue = computed(() => {
  return sampleRows.value.reduce((sum, row) => sum + Number(row.revenue || 0), 0)
})

const totalRevenueLabel = computed(() => {
  return String(overview.value?.metrics[0]?.value || formatCurrency(totalRevenue.value))
})

const sampleTrend = computed(() => {
  if (!sampleRows.value.length) return ''
  const points = sampleRows.value.slice(0, 8).map((row) => Number(row.revenue || 0)).reverse()
  const max = Math.max(...points)
  return points.map((value, index) => {
    const x = points.length === 1 ? 50 : (index / (points.length - 1)) * 100
    const y = 100 - (value / max) * 82
    return `${x},${y}`
  }).join(' ')
})

function chartPoints(chart: ChartPayload) {
  if (!chart.values.length) return ''
  const max = Math.max(...chart.values)
  return chart.values.map((value, index) => {
    const x = chart.values.length === 1 ? 50 : (index / (chart.values.length - 1)) * 100
    const y = 100 - (value / max) * 86
    return `${x},${y}`
  }).join(' ')
}

function barHeight(value: number, chart: ChartPayload) {
  const max = Math.max(...chart.values)
  return max ? Math.max((value / max) * 100, 8) : 0
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(value)
}

async function bootstrap() {
  try {
    await loginDemo()
    await refreshData()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nao foi possivel carregar os dados.'
  }
}

async function refreshData() {
  try {
    const [datasetList, sample, overviewData, alertList, reportList] = await Promise.all([
      listDatasets(),
      getSalesSample(),
      getOverview(),
      listAlerts(),
      listReports(),
    ])
    datasets.value = datasetList
    sampleRows.value = sample
    overview.value = overviewData
    alerts.value = alertList
    reports.value = reportList
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Nao foi possivel carregar os dados.'
  }
}

async function sendMessage() {
  if (!question.value.trim()) return
  const userMsg = question.value
  chatHistory.value.push({ id: Date.now(), role: 'user', text: userMsg })
  question.value = ''
  isTyping.value = true
  error.value = ''

  try {
    const analysis = await askQuestion(userMsg, chatId.value)
    chatId.value = analysis.chat_id
    chatHistory.value.push({
      id: Date.now(),
      role: 'ai',
      text: analysis.answer,
      analysis,
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erro ao consultar a API.'
  } finally {
    isTyping.value = false
  }
}

function askPreset(text: string) {
  question.value = text
  sendMessage()
}

function downloadCsv() {
  const token = localStorage.getItem('brainwave_token')
  fetch(exportUrl(), { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    .then((response) => response.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'brainwave-sales.csv'
      link.click()
      URL.revokeObjectURL(url)
    })
}

async function generateReport() {
  try {
    const report = await createReport(`Resumo executivo ${reports.value.length + 1}`)
    reports.value = [report, ...reports.value]
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erro ao gerar relatorio.'
  }
}

async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  isUploading.value = true
  uploadStatus.value = ''
  error.value = ''
  try {
    const result = await uploadSalesCsv(file, true)
    uploadStatus.value = `${result.imported_rows} linhas importadas de ${file.name}`
    await refreshData()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erro ao importar CSV.'
  } finally {
    isUploading.value = false
    input.value = ''
  }
}

onMounted(bootstrap)
</script>

<template>
  <section class="space-y-6">
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <article v-for="metric in dashboardMetrics" :key="metric.label" class="metric-card">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <small>{{ metric.helper }}</small>
      </article>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-12">
      <div class="space-y-6 xl:col-span-8">
        <section class="glass-card min-h-[470px]">
          <div class="relative z-10 mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p class="section-kicker">Analise principal</p>
              <h3 class="section-title">{{ latestAnalysis?.chart?.title || 'Performance comercial' }}</h3>
            </div>
            <div class="flex flex-wrap gap-2">
              <button class="quick-btn" @click="askPreset('Qual produto vendeu mais?')">Produtos</button>
              <button class="quick-btn" @click="askPreset('Mostre o faturamento por regiao')">Regioes</button>
              <button class="quick-btn" @click="askPreset('Como foi o faturamento mensal?')">Mensal</button>
            </div>
          </div>

          <div class="relative z-10 grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
            <div class="chart-stage">
              <template v-if="latestAnalysis?.chart">
                <svg
                  v-if="latestAnalysis.chart.type === 'line'"
                  viewBox="0 0 100 100"
                  preserveAspectRatio="none"
                  class="h-full w-full"
                >
                  <defs>
                    <linearGradient id="lineFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stop-color="#d4ad67" stop-opacity="0.52" />
                      <stop offset="100%" stop-color="#d4ad67" stop-opacity="0.02" />
                    </linearGradient>
                  </defs>
                  <polygon :points="`0,100 ${chartPoints(latestAnalysis.chart)} 100,100`" fill="url(#lineFill)" />
                  <polyline :points="chartPoints(latestAnalysis.chart)" fill="none" stroke="#f2d493" stroke-width="2.6" vector-effect="non-scaling-stroke" />
                </svg>

                <div v-else class="flex h-full items-end gap-5 px-2">
                  <div
                    v-for="(value, index) in latestAnalysis.chart.values"
                    :key="latestAnalysis.chart.labels[index]"
                    class="bar-column"
                  >
                    <div class="bar-fill" :style="{ height: `${barHeight(value, latestAnalysis.chart)}%` }"></div>
                    <span>{{ latestAnalysis.chart.labels[index] }}</span>
                  </div>
                </div>
              </template>

              <svg v-else viewBox="0 0 100 100" preserveAspectRatio="none" class="h-full w-full">
                <polyline :points="sampleTrend" fill="none" stroke="#f2d493" stroke-width="2.4" vector-effect="non-scaling-stroke" />
              </svg>
            </div>

            <aside class="insight-panel">
              <p class="section-kicker">Insights</p>
              <ul class="space-y-3">
                <li v-for="insight in latestAnalysis?.insights || ['Faca uma pergunta para gerar insights.', 'O SQL sera exibido com a tabela e o grafico.', 'Somente consultas SELECT sao permitidas.']" :key="insight">
                  {{ insight }}
                </li>
              </ul>
            </aside>
          </div>

          <div v-if="latestAnalysis" class="relative z-10 mt-6 grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
            <div class="sql-box">
              <span>SQL gerado</span>
              <pre>{{ latestAnalysis.sql }}</pre>
            </div>
            <div class="table-box">
              <table>
                <thead>
                  <tr>
                    <th v-for="column in latestAnalysis.columns" :key="column">{{ column }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in latestAnalysis.rows" :key="rowIndex">
                    <td v-for="column in latestAnalysis.columns" :key="column">{{ row[column] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section class="glass-card">
          <div class="relative z-10 flex items-center justify-between gap-4">
            <div>
              <p class="section-kicker">Chat analitico</p>
              <h3 class="section-title">Pergunte aos dados</h3>
            </div>
            <span class="status-dot">Seguro</span>
          </div>

          <div class="relative z-10 mt-5 max-h-72 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
            <div v-for="msg in chatHistory" :key="msg.id" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
              <p class="chat-bubble" :class="msg.role === 'user' ? 'user' : 'ai'">{{ msg.text }}</p>
            </div>
            <div v-if="isTyping" class="typing">Analisando dados...</div>
          </div>

          <p v-if="error" class="relative z-10 mt-4 rounded-lg border border-red-500/30 bg-red-950/30 px-4 py-3 text-sm text-red-200">{{ error }}</p>

          <div class="relative z-10 mt-5 flex gap-3">
            <input
              v-model="question"
              @keyup.enter="sendMessage"
              type="text"
              class="query-input"
              placeholder="Ex: qual categoria teve maior receita?"
            >
            <button class="send-btn" @click="sendMessage" aria-label="Enviar pergunta">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
              </svg>
            </button>
          </div>
        </section>
      </div>

      <aside class="space-y-6 xl:col-span-4">
        <section class="glass-card">
          <div class="relative z-10 flex items-center justify-between">
            <div>
              <p class="section-kicker">Datasets</p>
              <h3 class="section-title">Fontes ativas</h3>
            </div>
            <button class="export-btn" @click="downloadCsv">CSV</button>
          </div>

          <label class="upload-box relative z-10 mt-5">
            <input type="file" accept=".csv,text/csv" @change="handleUpload">
            <span>{{ isUploading ? 'Importando...' : 'Importar CSV de vendas' }}</span>
            <small>Colunas: order_date, region, category, product, quantity, unit_price</small>
          </label>
          <p v-if="uploadStatus" class="upload-status relative z-10">{{ uploadStatus }}</p>

          <div class="relative z-10 mt-4 space-y-4">
            <article v-for="dataset in datasets" :key="dataset.id" class="dataset-card">
              <div>
                <h4>{{ dataset.name }}</h4>
                <p>{{ dataset.description }}</p>
              </div>
              <span>{{ dataset.source }}</span>
            </article>
          </div>
        </section>

        <section class="glass-card">
          <div class="relative z-10">
            <p class="section-kicker">Retail sales</p>
            <h3 class="money-value">{{ totalRevenueLabel }}</h3>
            <div class="mini-bars">
              <div v-for="row in sampleRows.slice(0, 5)" :key="`${row.product}-${row.order_date}`" :style="{ height: `${Math.max((Number(row.revenue) / Math.max(totalRevenue, 1)) * 420, 18)}px` }"></div>
            </div>
          </div>
        </section>

        <section class="glass-card">
          <div class="relative z-10 flex items-center justify-between">
            <div>
              <p class="section-kicker">Alertas</p>
              <h3 class="section-title">Monitoramento</h3>
            </div>
            <span class="status-dot">{{ alerts.length }}</span>
          </div>
          <div class="relative z-10 mt-4 space-y-3">
            <article v-for="alert in alerts" :key="alert.id" class="alert-card">
              <div>
                <strong>{{ alert.title }}</strong>
                <span>{{ alert.metric }} {{ alert.operator }} {{ alert.threshold }}</span>
              </div>
              <em>{{ alert.status }}</em>
            </article>
          </div>
        </section>

        <section class="glass-card">
          <div class="relative z-10 flex items-center justify-between">
            <div>
              <p class="section-kicker">Relatorios</p>
              <h3 class="section-title">Executivos</h3>
            </div>
            <button class="export-btn" @click="generateReport">Gerar</button>
          </div>
          <div class="relative z-10 mt-4 space-y-3">
            <article v-for="report in reports.slice(0, 3)" :key="report.id" class="report-card">
              <strong>{{ report.title }}</strong>
              <span>{{ report.summary }}</span>
            </article>
            <p v-if="!reports.length" class="empty-state">Nenhum relatorio gerado ainda.</p>
          </div>
        </section>

        <section class="glass-card">
          <div class="relative z-10">
            <p class="section-kicker">Amostra</p>
            <h3 class="section-title">Ultimas vendas</h3>
            <div class="mt-4 max-h-72 overflow-auto custom-scrollbar">
              <table class="sample-table">
                <tbody>
                  <tr v-for="row in sampleRows" :key="`${row.product}-${row.order_date}`">
                    <td>
                      <strong>{{ row.product }}</strong>
                      <span>{{ row.region }}</span>
                    </td>
                    <td>{{ formatCurrency(Number(row.revenue || 0)) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.metric-card {
  border: 1px solid rgba(202, 163, 92, 0.34);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(20, 19, 14, 0.94), rgba(12, 12, 9, 0.94));
  min-height: 132px;
  padding: 24px;
  text-align: center;
}

.metric-card span,
.section-kicker {
  color: #d8bd82;
  display: block;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.metric-card strong {
  color: #fff7e6;
  display: block;
  font-size: clamp(24px, 4vw, 38px);
  font-weight: 400;
  margin-top: 14px;
}

.metric-card small {
  color: #9a927f;
  display: block;
  font-size: 11px;
  line-height: 1.4;
  margin-top: 10px;
}

.section-title {
  color: #fff7e6;
  font-size: 22px;
  font-weight: 600;
  margin-top: 4px;
}

.quick-btn,
.export-btn,
.status-dot {
  border: 1px solid rgba(202, 163, 92, 0.34);
  border-radius: 999px;
  color: #f2d493;
  font-size: 12px;
  padding: 8px 12px;
  transition: 0.2s;
}

.quick-btn:hover,
.export-btn:hover {
  background: rgba(202, 163, 92, 0.12);
  color: #fff7e6;
}

.chart-stage {
  border-bottom: 1px solid rgba(202, 163, 92, 0.18);
  height: 310px;
  padding: 22px 10px 30px;
}

.bar-column {
  align-items: center;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  justify-content: flex-end;
  min-width: 0;
}

.bar-fill {
  background: linear-gradient(180deg, #f2d493 0%, #8b6933 100%);
  border: 1px solid rgba(255, 247, 230, 0.22);
  box-shadow: 0 0 20px rgba(202, 163, 92, 0.18);
  width: 100%;
}

.bar-column span {
  color: #c9bea8;
  font-size: 11px;
  overflow: hidden;
  text-align: center;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.insight-panel,
.sql-box {
  border: 1px solid rgba(202, 163, 92, 0.22);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.22);
  padding: 18px;
}

.insight-panel li {
  color: #d5c9ad;
  font-size: 14px;
  line-height: 1.5;
}

.sql-box span {
  color: #d8bd82;
  font-size: 12px;
  text-transform: uppercase;
}

.sql-box pre {
  color: #fff7e6;
  font-size: 12px;
  margin-top: 10px;
  white-space: pre-wrap;
}

.table-box {
  border: 1px solid rgba(202, 163, 92, 0.22);
  border-radius: 8px;
  max-height: 220px;
  overflow: auto;
}

.table-box table,
.sample-table {
  width: 100%;
}

.table-box th,
.table-box td {
  border-bottom: 1px solid rgba(202, 163, 92, 0.16);
  color: #d5c9ad;
  font-size: 12px;
  padding: 10px 12px;
  text-align: left;
}

.table-box th {
  color: #f2d493;
  font-weight: 500;
}

.chat-bubble {
  border: 1px solid rgba(202, 163, 92, 0.22);
  border-radius: 8px;
  max-width: 82%;
  padding: 12px 14px;
}

.chat-bubble.ai {
  background: rgba(0, 0, 0, 0.28);
  color: #d5c9ad;
}

.chat-bubble.user {
  background: rgba(202, 163, 92, 0.14);
  color: #fff7e6;
}

.typing {
  color: #d8bd82;
  font-size: 13px;
}

.query-input {
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(202, 163, 92, 0.28);
  border-radius: 999px;
  color: #fff7e6;
  flex: 1;
  min-width: 0;
  padding: 14px 18px;
}

.query-input:focus {
  border-color: rgba(242, 212, 147, 0.74);
  outline: none;
}

.send-btn {
  align-items: center;
  background: linear-gradient(135deg, #f2d493, #b88a43);
  border-radius: 999px;
  color: #090907;
  display: flex;
  height: 48px;
  justify-content: center;
  width: 48px;
}

.dataset-card {
  align-items: flex-start;
  border: 1px solid rgba(202, 163, 92, 0.18);
  border-radius: 8px;
  display: flex;
  gap: 14px;
  justify-content: space-between;
  padding: 16px;
}

.upload-box {
  border: 1px dashed rgba(202, 163, 92, 0.34);
  border-radius: 8px;
  cursor: pointer;
  display: block;
  padding: 16px;
  transition: 0.2s;
}

.upload-box:hover {
  background: rgba(202, 163, 92, 0.08);
  border-color: rgba(242, 212, 147, 0.62);
}

.upload-box input {
  height: 1px;
  opacity: 0;
  position: absolute;
  width: 1px;
}

.upload-box span {
  color: #fff7e6;
  display: block;
  font-size: 13px;
  font-weight: 600;
}

.upload-box small,
.upload-status {
  color: #9a927f;
  display: block;
  font-size: 12px;
  line-height: 1.45;
  margin-top: 6px;
}

.upload-status {
  color: #f2d493;
}

.dataset-card h4 {
  color: #fff7e6;
  font-weight: 600;
}

.alert-card,
.report-card {
  border: 1px solid rgba(202, 163, 92, 0.18);
  border-radius: 8px;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  padding: 14px;
}

.alert-card strong,
.report-card strong {
  color: #fff7e6;
  display: block;
  font-size: 13px;
}

.alert-card span,
.report-card span,
.empty-state {
  color: #9a927f;
  display: block;
  font-size: 12px;
  line-height: 1.45;
  margin-top: 4px;
}

.alert-card em {
  color: #f2d493;
  flex: 0 0 auto;
  font-size: 12px;
  font-style: normal;
  text-transform: uppercase;
}

.report-card {
  display: block;
}

.dataset-card p,
.dataset-card span,
.sample-table span {
  color: #9a927f;
  font-size: 12px;
}

.money-value {
  color: #fff7e6;
  font-size: clamp(34px, 5vw, 50px);
  font-weight: 300;
  margin-top: 10px;
}

.mini-bars {
  align-items: end;
  border-bottom: 1px solid rgba(202, 163, 92, 0.18);
  display: flex;
  gap: 14px;
  height: 155px;
  justify-content: center;
  margin-top: 22px;
}

.mini-bars div {
  background: linear-gradient(180deg, #f2d493, #8b6933);
  border: 1px solid rgba(255, 247, 230, 0.18);
  width: 28px;
}

.sample-table td {
  border-bottom: 1px solid rgba(202, 163, 92, 0.14);
  padding: 12px 0;
}

.sample-table strong {
  color: #fff7e6;
  display: block;
  font-size: 13px;
}

.sample-table td:last-child {
  color: #f2d493;
  font-size: 13px;
  text-align: right;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.2);
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(202, 163, 92, 0.34);
  border-radius: 10px;
}
</style>
