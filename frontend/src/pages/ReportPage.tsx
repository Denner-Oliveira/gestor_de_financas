import { useEffect, useState, type SubmitEvent } from 'react'
import type { GeneralReport } from '../types/finance'
import { fetchGeneralReport } from '../services/api'
import { formatCurrency } from '../utils/format'

type Props = { email: string; onBack: () => void; onLogout: () => void }
type ChartMetric = 'receitas' | 'despesas' | 'saldo'
type ChartGrouping = 'mes' | 'categoria' | 'conta'
type ChartType = 'pizza' | 'barras' | 'colunas' | 'linha'

type ChartItem = { label: string; value: number }

function polarPoint(cx: number, cy: number, radiusX: number, radiusY: number, angle: number) {
  const radians = (angle - 90) * Math.PI / 180
  return { x: cx + radiusX * Math.cos(radians), y: cy + radiusY * Math.sin(radians) }
}

function slicePath(cx: number, cy: number, radiusX: number, radiusY: number, start: number, end: number) {
  const startPoint = polarPoint(cx, cy, radiusX, radiusY, end)
  const endPoint = polarPoint(cx, cy, radiusX, radiusY, start)
  const largeArc = end - start > 180 ? 1 : 0
  return `M ${cx} ${cy} L ${startPoint.x} ${startPoint.y} A ${radiusX} ${radiusY} 0 ${largeArc} 0 ${endPoint.x} ${endPoint.y} Z`
}

function darkenColor(color: string) {
  const value = color.slice(1)
  const channels = [0, 2, 4].map((index) => Math.max(0, Number.parseInt(value.slice(index, index + 2), 16) - 45))
  return `#${channels.map((channel) => channel.toString(16).padStart(2, '0')).join('')}`
}

function PieChart({ items, colors }: { items: ChartItem[]; colors: string[] }) {
  const total = Math.max(items.reduce((sum, item) => sum + Math.abs(item.value), 0), 1)
  const smallItems = items.filter((item) => Math.abs(item.value) / total < 0.05)
  const displayItems = smallItems.length > 0
    ? [
      ...items.filter((item) => Math.abs(item.value) / total >= 0.05),
      { label: 'Outros', value: smallItems.reduce((sum, item) => sum + item.value, 0) },
    ]
    : items
  const displayTotal = Math.max(displayItems.reduce((sum, item) => sum + Math.abs(item.value), 0), 1)
  const slices = displayItems.map((item, index) => {
    const start = displayItems
      .slice(0, index)
      .reduce((angle, previous) => angle + Math.abs(previous.value) / displayTotal * 360, 0)
    const end = start + Math.abs(item.value) / displayTotal * 360
    const middle = (start + end) / 2
    const point = polarPoint(200, 142, 112, 62, middle)
    const labelPoint = polarPoint(200, 142, 150, 88, middle)
    const right = labelPoint.x >= 200
    return {
      ...item,
      start,
      end,
      point,
      labelPoint: { ...labelPoint, x: right ? 330 : 70 },
      right,
      color: colors[index % colors.length],
    }
  })

  return <div className="pie-layout">
    <svg className="pie-chart-svg" viewBox="0 0 400 330" role="img" aria-label="Gráfico de pizza com distribuição dos valores">
      <defs>
        <filter id="pie-shadow" x="-20%" y="-20%" width="140%" height="160%">
          <feDropShadow dx="0" dy="8" stdDeviation="7" floodColor="#0f172a" floodOpacity="0.18" />
        </filter>
      </defs>
      <g filter="url(#pie-shadow)">
        {Array.from({ length: 16 }, (_, depth) => <g key={`depth-${depth}`} transform={`translate(0 ${depth * 1.5})`}>{slices.map((slice) => <path key={`depth-${depth}-${slice.label}`} d={slicePath(200, 142, 112, 62, slice.start, slice.end)} fill={darkenColor(slice.color)} stroke="#ffffff" strokeWidth="1" />)}</g>)}
        {slices.map((slice) => <path key={slice.label} d={slicePath(200, 142, 112, 62, slice.start, slice.end)} fill={slice.color} stroke="#ffffff" strokeWidth="2" />)}
      </g>
      {slices.map((slice) => <g key={`label-${slice.label}`}>
        <polyline points={`${slice.point.x},${slice.point.y} ${slice.labelPoint.x},${slice.labelPoint.y} ${slice.right ? slice.labelPoint.x + 8 : slice.labelPoint.x - 8},${slice.labelPoint.y}`} fill="none" stroke="#94a3b8" strokeWidth="1.5" />
        <circle cx={slice.point.x} cy={slice.point.y} r="3" fill={slice.color} stroke="#ffffff" strokeWidth="1" />
        <text x={slice.labelPoint.x + (slice.right ? 12 : -12)} y={slice.labelPoint.y - 3} textAnchor={slice.right ? 'start' : 'end'} className="pie-label">{slice.label}</text>
        <text x={slice.labelPoint.x + (slice.right ? 12 : -12)} y={slice.labelPoint.y + 12} textAnchor={slice.right ? 'start' : 'end'} className="pie-label-value">{formatCurrency(slice.value)}</text>
      </g>)}
    </svg>
  </div>
}

export function ReportPage({ email, onBack, onLogout }: Props) {
  const now = new Date()
  const [inicio, setInicio] = useState(`${now.getFullYear()}-01-01`)
  const [fim, setFim] = useState(now.toISOString().slice(0, 10))
  const [report, setReport] = useState<GeneralReport | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [chartMetric, setChartMetric] = useState<ChartMetric>('despesas')
  const [chartGrouping, setChartGrouping] = useState<ChartGrouping>('mes')
  const [chartType, setChartType] = useState<ChartType>('pizza')

  async function loadReport(event?: SubmitEvent<HTMLFormElement>) {
    event?.preventDefault()
    setLoading(true)
    setError('')
    try {
      setReport(await fetchGeneralReport(inicio, fim))
    } catch (loadError) {
      if (loadError instanceof Error && loadError.message === 'UNAUTHORIZED') {
        onLogout()
      } else {
        setError(loadError instanceof Error ? loadError.message : 'Não foi possível carregar o relatório.')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadReport()
  }, [])

  const chartItems = report
    ? chartGrouping === 'mes'
      ? report.por_mes.map((item) => ({
        label: item.mes,
        value: chartMetric === 'receitas'
          ? Number(item.receitas)
          : chartMetric === 'despesas'
            ? Number(item.despesas)
            : Number(item.receitas) - Number(item.despesas),
      }))
      : chartGrouping === 'categoria'
        ? report.por_categoria.map((item) => ({ label: item.categoria, value: Number(item.valor) }))
        : report.por_conta
          .filter((item) => Number(item.receitas) || Number(item.despesas))
          .map((item) => ({
            label: item.conta,
            value: chartMetric === 'receitas'
              ? Number(item.receitas)
              : chartMetric === 'despesas'
                ? Number(item.despesas)
                : Number(item.receitas) - Number(item.despesas),
          }))
    : []
  const chartMax = Math.max(...chartItems.map((item) => Math.abs(item.value)), 1)
  const chartColors = ['#2563eb', '#16a34a', '#f97316', '#9333ea', '#dc2626', '#0891b2', '#ca8a04']

  return <main className="app-shell dashboard-shell">
    <nav className="topbar dashboard-topbar">
      <strong className="brand">Finanças</strong>
      <div className="app-tabs" role="tablist" aria-label="Navegação principal">
        <button type="button" className="app-tab" onClick={onBack}>Visão geral</button>
        <button type="button" className="app-tab active" role="tab" aria-selected="true">Relatório geral</button>
      </div>
      <div className="report-nav-actions">
        <span className="report-user">{email}</span>
        <button type="button" className="link-button" onClick={onLogout}>Sair</button>
      </div>
    </nav>
    <section className="dashboard-content report-page">
      <div className="dashboard-heading">
        <div><span className="eyebrow">ANÁLISE</span><h1>Relatório geral</h1><p className="report-description">Consulte suas receitas e despesas em qualquer período.</p></div>
      </div>
      <form className="report-filters" onSubmit={loadReport}>
        <label>Data inicial<input type="date" value={inicio} onChange={(event) => setInicio(event.target.value)} required /></label>
        <label>Data final<input type="date" value={fim} onChange={(event) => setFim(event.target.value)} required /></label>
        <button type="submit" disabled={loading}>{loading ? 'Carregando...' : 'Atualizar relatório'}</button>
      </form>
      {error && <p className="form-error">{error}</p>}
      {report && <><div className="report-grid report-summary">
        <article className="report-card"><span>Receitas</span><strong className="income">{formatCurrency(Number(report.totais.receitas))}</strong></article>
        <article className="report-card"><span>Despesas</span><strong className="expense">{formatCurrency(Number(report.totais.despesas))}</strong></article>
        <article className="report-card"><span>Saldo do período</span><strong className={Number(report.totais.saldo) >= 0 ? 'income' : 'expense'}>{formatCurrency(Number(report.totais.saldo))}</strong></article>
      </div><div className="report-columns report-details">
        <div><h2>Totais por conta</h2>{report.por_conta.filter((item) => Number(item.receitas) || Number(item.despesas)).map((item) => <div className="report-row" key={item.conta}><span>{item.conta}</span><strong className={Number(item.receitas) - Number(item.despesas) >= 0 ? 'income' : 'expense'}>{formatCurrency(Number(item.receitas) - Number(item.despesas))}</strong></div>)}</div>
        <div><h2>Despesas por categoria</h2>{report.por_categoria.map((item) => <div className="report-row" key={item.categoria}><span>{item.categoria}</span><strong className="expense">{formatCurrency(Number(item.valor))}</strong></div>)}</div>
      </div><section className="report-chart-section"><div className="chart-heading"><div><h2>Gráficos interativos</h2><p>Altere o tipo, a métrica e o agrupamento para explorar o período.</p></div><div className="chart-controls"><label>Tipo de gráfico<select value={chartType} onChange={(event) => setChartType(event.target.value as ChartType)}><option value="pizza">Pizza</option><option value="barras">Barras horizontais</option><option value="colunas">Colunas</option><option value="linha">Linha</option></select></label><label>Métrica<select value={chartMetric} onChange={(event) => setChartMetric(event.target.value as ChartMetric)}><option value="despesas">Despesas</option><option value="receitas">Receitas</option><option value="saldo">Saldo</option></select></label><label>Agrupar por<select value={chartGrouping} onChange={(event) => setChartGrouping(event.target.value as ChartGrouping)}><option value="mes">Mês</option><option value="categoria">Categoria</option><option value="conta">Conta</option></select></label></div></div>{chartItems.length === 0 ? <p className="empty-state chart-empty">Não há dados para o gráfico neste período.</p> : chartType === 'pizza' ? <PieChart items={chartItems} colors={chartColors} /> : chartType === 'linha' ? <div className="line-chart">{chartItems.map((item, index) => <div className="line-point" key={item.label} style={{ left: `${chartItems.length === 1 ? 50 : index / (chartItems.length - 1) * 100}%`, bottom: `${Math.max(Math.abs(item.value) / chartMax * 180, 8)}px` }}><span>{formatCurrency(item.value)}</span><i /><small>{item.label}</small></div>)}</div> : <div className={`chart-bars ${chartType === 'barras' ? 'horizontal-bars' : ''}`}>{chartItems.map((item) => <div className="chart-bar-item" key={item.label}><div className="chart-value">{formatCurrency(item.value)}</div><div className={`chart-bar ${item.value < 0 ? 'negative' : ''}`} style={chartType === 'barras' ? { width: `${Math.max(Math.abs(item.value) / chartMax * 100, 4)}%` } : { height: `${Math.max(Math.abs(item.value) / chartMax * 180, 8)}px` }} title={`${item.label}: ${formatCurrency(item.value)}`} /><span>{item.label}</span></div>)}</div>}</section><section className="report-chart-section"><div className="chart-heading"><div><h2>Despesas por categoria</h2><p>Distribuição das despesas no período selecionado.</p></div></div><div className="category-bars">{report.por_categoria.length === 0 ? <p className="empty-state">Não há despesas categorizadas.</p> : report.por_categoria.map((item) => { const width = Math.max(Number(item.valor) / Math.max(...report.por_categoria.map((category) => Number(category.valor)), 1) * 100, 4); return <div className="category-bar-item" key={item.categoria}><div><span>{item.categoria}</span><strong className="expense">{formatCurrency(Number(item.valor))}</strong></div><div className="category-bar-track"><div className="category-bar-fill" style={{ width: `${width}%` }} /></div></div>})}</div></section><section className="report-table-section"><h2>Resumo mensal</h2><div className="report-month-list">{report.por_mes.map((item) => <div className="report-row" key={item.mes}><span>{item.mes}</span><span><strong className="income">+ {formatCurrency(Number(item.receitas))}</strong> <strong className="expense">− {formatCurrency(Number(item.despesas))}</strong></span></div>)}</div></section></>}
    </section>
  </main>
}
