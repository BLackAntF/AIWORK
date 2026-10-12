<template>
  <div class="admin-model-compare">
    <div class="page-header">
      <h2 class="page-title">模型版本对比</h2>
      <p class="page-subtitle">各模型版本检测效果与类别分布横向对比</p>
    </div>

    <el-empty v-if="loaded && !versions.length" description="暂无模型版本数据" />

    <template v-else>
      <div v-loading="loading" class="version-cards">
        <el-card v-for="v in versions" :key="v.model_version" shadow="hover" class="version-card">
          <div class="v-name">{{ v.model_version }}</div>
          <div class="v-total">
            <span class="v-num">{{ formatNumber(v.total) }}</span>
            <span class="v-unit">次检测</span>
          </div>
          <el-progress :percentage="diseaseRate(v)" :stroke-width="8" :color="accentColor" />
          <div class="v-rate">
            <span>病害 {{ rateText(v, 'disease_count') }} · 健康 {{ rateText(v, 'healthy_count') }}</span>
            <span class="v-nodetect">无检出 {{ v.no_detection }}</span>
          </div>
          <div class="v-meta">平均置信度：<b>{{ confText(v) }}</b></div>
          <div class="v-meta">使用时段：{{ useRange(v) }}</div>
        </el-card>
      </div>

      <div class="glass-card table-card">
        <h3 class="card-title">版本对比明细</h3>
        <el-table v-loading="loading" :data="versions" stripe>
          <el-table-column prop="model_version" label="版本" min-width="140" show-overflow-tooltip />
          <el-table-column prop="total" label="检测数" width="90" align="center" />
          <el-table-column prop="disease_count" label="病害数" width="90" align="center" />
          <el-table-column prop="healthy_count" label="健康数" width="90" align="center" />
          <el-table-column prop="no_detection" label="无检出" width="90" align="center" />
          <el-table-column label="平均置信度" width="110" align="center">
            <template #default="{ row }">{{ confText(row) }}</template>
          </el-table-column>
          <el-table-column label="最早使用" width="160">
            <template #default="{ row }">{{ timeText(row.first_used) }}</template>
          </el-table-column>
          <el-table-column label="最近使用" width="160">
            <template #default="{ row }">{{ timeText(row.last_used) }}</template>
          </el-table-column>
        </el-table>
      </div>

      <div class="glass-card chart-card">
        <h3 class="card-title">类别检出分布对比</h3>
        <el-empty v-if="chartEmpty" description="暂无类别检出数据" :image-size="90" />
        <div v-else ref="distChartRef" class="chart-container"></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getModelCompare } from '@/api/admin'
import { formatNumber, formatPercent, formatTime } from '@/utils/format'

const TOP_CLASS_COUNT = 8
const DEFAULT_ACCENT = '#c96247'
const SERIES_COLORS = ['#c96247', '#3a7d55', '#d9a11e', '#4e7a6d', '#a6694f', '#5b665f', '#8a938c', '#c73e2d']

const versions = ref([])
const loading = ref(false)
const loaded = ref(false)
const chartEmpty = ref(true)
const accentColor = ref(DEFAULT_ACCENT)
const distChartRef = ref(null)
let distChart = null

function resolveAccent() {
  const value = getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim()
  if (value) accentColor.value = value
}

function diseaseRate(v) {
  return v.total ? Math.round((v.disease_count / v.total) * 100) : 0
}

function rateText(v, key) {
  return v.total ? formatPercent(v[key] / v.total, 1) : '0.0%'
}

function confText(v) {
  return v.avg_confidence == null ? '—' : formatPercent(v.avg_confidence, 1)
}

function timeText(value) {
  return value ? formatTime(value, 'YYYY-MM-DD HH:mm') : '—'
}

function useRange(v) {
  return (v.first_used || v.last_used) ? `${timeText(v.first_used)} ~ ${timeText(v.last_used)}` : '—'
}

function topClasses(v) {
  return (v.class_distribution || []).slice(0, TOP_CLASS_COUNT)
}

function collectClasses(list) {
  const classSet = new Set()
  list.forEach(v => topClasses(v).forEach(([name]) => classSet.add(name)))
  return [...classSet]
}

function buildBarSeries(list, classes) {
  return list.map((v, idx) => ({
    name: v.model_version,
    type: 'bar',
    data: classes.map(name => topClasses(v).find(([n]) => n === name)?.[1] || 0),
    itemStyle: { color: SERIES_COLORS[idx % SERIES_COLORS.length], borderRadius: [4, 4, 0, 0] }
  }))
}

function buildDistOption(list, classes) {
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0, textStyle: { color: 'var(--color-text-secondary)' } },
    grid: { left: '3%', right: '4%', top: '18%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: classes,
      axisLine: { lineStyle: { color: 'var(--color-border)' } },
      axisLabel: { color: 'var(--color-text-secondary)', rotate: 30, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'var(--color-border)', type: 'dashed' } },
      axisLabel: { color: 'var(--color-text-secondary)', fontSize: 11 }
    },
    series: buildBarSeries(list, classes)
  }
}

function renderDistChart() {
  const classes = collectClasses(versions.value)
  distChart = echarts.init(distChartRef.value)
  distChart.setOption(buildDistOption(versions.value, classes))
}

async function fetchCompare() {
  loading.value = true
  try {
    const data = await getModelCompare()
    versions.value = data.versions || []
    chartEmpty.value = !versions.value.some(v => (v.class_distribution || []).length)
    if (!chartEmpty.value) {
      await nextTick()
      renderDistChart()
    }
  } catch (e) {
    console.error('获取模型对比数据失败', e)
  } finally {
    loading.value = false
    loaded.value = true
  }
}

function handleResize() {
  distChart?.resize()
}

onMounted(async () => {
  resolveAccent()
  await fetchCompare()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  distChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.admin-model-compare {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.version-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
  min-height: 120px;
}

.version-card :deep(.el-card__body) {
  padding: 18px 20px;
}

.v-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  word-break: break-all;
}

.v-total {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 10px;
}

.v-num {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-accent);
  font-variant-numeric: tabular-nums;
}

.v-unit {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.v-rate {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 6px 0 10px;
}

.v-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.9;
}

.v-meta b {
  color: var(--color-text-primary);
}

.table-card {
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.chart-card {
  padding: 20px;
  border-radius: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px;
}

.chart-container {
  width: 100%;
  height: 360px;
}

@media (max-width: 640px) {
  .chart-container {
    height: 280px;
  }
}
</style>
