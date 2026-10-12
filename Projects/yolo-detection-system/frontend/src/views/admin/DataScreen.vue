<template>
  <div class="data-screen">
    <header class="screen-header">
      <div>
        <h1 class="screen-title">番茄病害检测系统 · 数据大屏</h1>
        <p class="screen-sub">TOMATO DISEASE DETECTION · REALTIME MONITOR</p>
      </div>
      <div class="header-right">
        <div class="clock">
          <div class="clock-time">{{ clockTime }}</div>
          <div class="clock-date">{{ clockDate }}</div>
        </div>
        <button class="fs-btn" type="button" @click="toggleFullscreen">
          {{ isFullscreen ? '退出全屏' : '进入全屏' }}
        </button>
      </div>
    </header>

    <section class="stat-row">
      <div v-for="card in statCards" :key="card.label" class="stat-card">
        <div class="stat-value">{{ card.value }}</div>
        <div class="stat-label">{{ card.label }}</div>
      </div>
    </section>

    <section class="chart-grid">
      <div class="chart-panel">
        <h3 class="panel-title">近 7 天检测趋势</h3>
        <div v-if="chartState.trend === 'ready'" ref="trendChartRef" class="chart-box"></div>
        <div v-else-if="chartState.trend === 'loading'" class="chart-loading"></div>
        <el-empty v-else description="暂无检测数据" :image-size="72" />
      </div>

      <div class="chart-panel">
        <h3 class="panel-title">病害类别分布</h3>
        <div v-if="chartState.pie === 'ready'" ref="pieChartRef" class="chart-box"></div>
        <div v-else-if="chartState.pie === 'loading'" class="chart-loading"></div>
        <el-empty v-else description="暂无病害数据" :image-size="72" />
      </div>

      <div class="chart-panel">
        <h3 class="panel-title">近 7 天用户增长</h3>
        <div v-if="chartState.users === 'ready'" ref="usersChartRef" class="chart-box"></div>
        <div v-else-if="chartState.users === 'loading'" class="chart-loading"></div>
        <el-empty v-else description="暂无用户数据" :image-size="72" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats, getUsersTrend, getDetectionsTrend, getDiseaseDistribution } from '@/api/admin'
import { formatTime, formatNumber } from '@/utils/format'

const TREND_DAYS = 7
const DISTRIBUTION_DAYS = 30
const TOP_CLASS_COUNT = 10
const DEFAULT_ACCENT = '#c96247'
const EMPTY_TEXT = '--'
const WEEK_LABELS = ['日', '一', '二', '三', '四', '五', '六']
const SERIES_COLORS = ['#c96247', '#e0885a', '#d9a11e', '#3a7d55', '#4e7a6d', '#5b8fa8', '#a6694f', '#8a938c', '#c73e2d', '#7d6b94']
const CHART_THEME = {
  bg: '#0d1424',
  axis: 'rgba(255,255,255,0.14)',
  splitLine: 'rgba(255,255,255,0.07)',
  textDim: 'rgba(232,236,246,0.6)',
  tooltipBg: 'rgba(18,26,48,0.92)',
  tooltipBorder: 'rgba(255,255,255,0.12)'
}

const now = ref(new Date())
const dashboard = ref(null)
const isFullscreen = ref(false)
const accent = ref(DEFAULT_ACCENT)
const chartState = reactive({ trend: 'loading', pie: 'loading', users: 'loading' })
const trendChartRef = ref(null)
const pieChartRef = ref(null)
const usersChartRef = ref(null)
let clockTimer = null
let trendChart = null
let pieChart = null
let usersChart = null

const clockTime = computed(() => formatTime(now.value, 'YYYY-MM-DD HH:mm:ss'))
const clockDate = computed(() => `星期${WEEK_LABELS[now.value.getDay()]}`)

const statCards = computed(() => {
  const d = dashboard.value || {}
  return [
    { label: '用户总数', value: numText(d.total_users) },
    { label: '检测总数', value: numText(d.total_detections) },
    { label: '知识库条数', value: numText(d.total_knowledge) },
    { label: '今日检测', value: numText(d.today_detections) }
  ]
})

function numText(value) {
  return value == null ? EMPTY_TEXT : formatNumber(value)
}

function resolveAccent() {
  const value = getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim()
  if (value) accent.value = value
}

function startClock() {
  clockTimer = window.setInterval(() => {
    now.value = new Date()
  }, 1000)
}

function darkTooltip() {
  return {
    backgroundColor: CHART_THEME.tooltipBg,
    borderColor: CHART_THEME.tooltipBorder,
    textStyle: { color: '#e8ecf6' }
  }
}

function areaAxes(dates) {
  return {
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: CHART_THEME.axis } },
      axisLabel: { color: CHART_THEME.textDim, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: CHART_THEME.splitLine } },
      axisLabel: { color: CHART_THEME.textDim, fontSize: 11 }
    }
  }
}

function areaSeries(counts, name) {
  const color = accent.value
  return [{
    name,
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    data: counts,
    lineStyle: { width: 2, color },
    itemStyle: { color },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: color + '55' },
        { offset: 1, color: color + '05' }
      ])
    }
  }]
}

function buildAreaOption(dates, counts, name) {
  return {
    tooltip: { trigger: 'axis', ...darkTooltip() },
    grid: { left: '3%', right: '4%', top: '12%', bottom: '6%', containLabel: true },
    ...areaAxes(dates),
    series: areaSeries(counts, name)
  }
}

function buildPieSeries(entries) {
  return [{
    type: 'pie',
    radius: ['42%', '68%'],
    center: ['36%', '50%'],
    itemStyle: { borderRadius: 6, borderColor: CHART_THEME.bg, borderWidth: 2 },
    label: { show: false },
    labelLine: { show: false },
    data: entries.map((entry, idx) => ({
      name: entry.name,
      value: entry.value,
      itemStyle: { color: SERIES_COLORS[idx % SERIES_COLORS.length] }
    }))
  }]
}

function buildPieOption(entries) {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', ...darkTooltip() },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 0,
      top: 'middle',
      textStyle: { color: CHART_THEME.textDim, fontSize: 11 },
      pageIconColor: CHART_THEME.textDim,
      pageTextStyle: { color: CHART_THEME.textDim }
    },
    series: buildPieSeries(entries)
  }
}

function initChart(instance, el) {
  if (instance) instance.dispose()
  return el ? echarts.init(el) : null
}

async function loadTrendChart() {
  try {
    const data = await getDetectionsTrend(TREND_DAYS)
    if (!(data.dates || []).length) {
      chartState.trend = 'empty'
      return
    }
    chartState.trend = 'ready'
    await nextTick()
    trendChart = initChart(trendChart, trendChartRef.value)
    trendChart?.setOption(buildAreaOption(data.dates, data.counts || [], '检测量'))
  } catch (e) {
    chartState.trend = 'empty'
    console.error('加载检测趋势失败', e)
  }
}

async function loadUsersChart() {
  try {
    const data = await getUsersTrend(TREND_DAYS)
    if (!(data.cumulative || []).length) {
      chartState.users = 'empty'
      return
    }
    chartState.users = 'ready'
    await nextTick()
    usersChart = initChart(usersChart, usersChartRef.value)
    usersChart?.setOption(buildAreaOption(data.dates || [], data.cumulative, '累计用户'))
  } catch (e) {
    chartState.users = 'empty'
    console.error('加载用户趋势失败', e)
  }
}

async function loadPieChart() {
  try {
    const data = await getDiseaseDistribution(DISTRIBUTION_DAYS)
    const entries = Object.entries(data.distribution || {})
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, TOP_CLASS_COUNT)
    if (!entries.length) {
      chartState.pie = 'empty'
      return
    }
    chartState.pie = 'ready'
    await nextTick()
    pieChart = initChart(pieChart, pieChartRef.value)
    pieChart?.setOption(buildPieOption(entries))
  } catch (e) {
    chartState.pie = 'empty'
    console.error('加载病害分布失败', e)
  }
}

async function loadStats() {
  try {
    dashboard.value = await getDashboardStats()
  } catch (e) {
    console.error('加载统计概览失败', e)
  }
}

async function toggleFullscreen() {
  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen()
    } else {
      await document.documentElement.requestFullscreen()
    }
  } catch (e) {
    console.error('全屏切换失败', e)
  }
}

function handleFullscreenChange() {
  isFullscreen.value = Boolean(document.fullscreenElement)
  handleResize()
}

function handleResize() {
  trendChart?.resize()
  pieChart?.resize()
  usersChart?.resize()
}

onMounted(() => {
  resolveAccent()
  startClock()
  loadStats()
  loadTrendChart()
  loadPieChart()
  loadUsersChart()
  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  if (clockTimer) window.clearInterval(clockTimer)
  trendChart?.dispose()
  pieChart?.dispose()
  usersChart?.dispose()
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
.data-screen {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 26px 34px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  color: #e8ecf6;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
  background:
    radial-gradient(1000px 460px at 80% -10%, rgba(201, 98, 71, 0.16), transparent 62%),
    radial-gradient(820px 420px at 4% 112%, rgba(78, 122, 109, 0.12), transparent 60%),
    linear-gradient(180deg, #0d1424 0%, #0a101f 100%);
}

.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.screen-title {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 3px;
  color: #f4ede6;
  background: linear-gradient(90deg, #f4ede6 0%, #c96247 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.screen-sub {
  margin: 4px 0 0;
  font-size: 12px;
  letter-spacing: 4px;
  color: rgba(232, 236, 246, 0.4);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 18px;
}

.clock {
  text-align: right;
}

.clock-time {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  font-variant-numeric: tabular-nums;
}

.clock-date {
  margin-top: 2px;
  font-size: 12px;
  color: rgba(232, 236, 246, 0.5);
}

.fs-btn {
  padding: 8px 18px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.06);
  color: #e8ecf6;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.fs-btn:hover {
  border-color: #c96247;
  color: #e0885a;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  padding: 22px 24px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #c96247;
}

.stat-value {
  font-size: 34px;
  font-weight: 800;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  margin-top: 8px;
  font-size: 13px;
  letter-spacing: 1px;
  color: rgba(232, 236, 246, 0.55);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  flex: 1;
}

.chart-panel {
  padding: 18px 20px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  min-width: 0;
}

.panel-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.2;
  padding-left: 10px;
  border-left: 3px solid #c96247;
}

.chart-box {
  width: 100%;
  height: clamp(260px, 34vh, 400px);
}

.chart-loading {
  height: clamp(260px, 34vh, 400px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading::after {
  content: '';
  width: 26px;
  height: 26px;
  border: 3px solid rgba(255, 255, 255, 0.15);
  border-top-color: #c96247;
  border-radius: 50%;
  animation: screen-spin 0.8s linear infinite;
}

@keyframes screen-spin {
  to {
    transform: rotate(360deg);
  }
}

.data-screen :deep(.el-empty__description p) {
  color: rgba(232, 236, 246, 0.45);
}

@media (max-width: 1200px) {
  .data-screen {
    padding: 20px;
  }

  .stat-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
