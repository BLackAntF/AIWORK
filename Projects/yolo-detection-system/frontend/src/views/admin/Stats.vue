<template>
  <div class="admin-stats">
    <div class="page-header">
      <h2 class="page-title">数据统计</h2>
      <p class="page-subtitle">系统运行数据可视化分析</p>
    </div>

    <div class="period-bar glass-card">
      <span class="period-label">统计周期：</span>
      <el-radio-group v-model="periodDays" size="default" @change="fetchAllStats">
        <el-radio-button :value="7">近7天</el-radio-button>
        <el-radio-button :value="30">近30天</el-radio-button>
        <el-radio-button :value="90">近90天</el-radio-button>
      </el-radio-group>
      <el-button type="primary" :icon="Download" class="export-btn" @click="handleExport">导出报表</el-button>
    </div>

    <div class="charts-grid">
      <div class="chart-card glass-card">
        <div class="chart-header">
          <h3 class="chart-title">用户增长趋势</h3>
        </div>
        <div ref="usersChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card glass-card">
        <div class="chart-header">
          <h3 class="chart-title">检测量趋势</h3>
        </div>
        <div ref="detectionsChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card glass-card full-width">
        <div class="chart-header">
          <h3 class="chart-title">知识库分类分布</h3>
        </div>
        <div ref="knowledgeChartRef" class="chart-container pie-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import {
  getUsersTrend, getDetectionsTrend, getKnowledgeStats, exportStats
} from '@/api/admin'

const periodDays = ref(7)
const usersChartRef = ref(null)
const detectionsChartRef = ref(null)
const knowledgeChartRef = ref(null)
let usersChart = null
let detectionsChart = null
let knowledgeChart = null

function getAccentColor() {
  return getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim()
}

function getLineOptions(xData, yData, name) {
  const accent = getAccentColor()
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xData,
      axisLine: { lineStyle: { color: 'var(--color-border)' } },
      axisLabel: { color: 'var(--color-text-secondary)', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'var(--color-border)', type: 'dashed' } },
      axisLabel: { color: 'var(--color-text-secondary)', fontSize: 11 }
    },
    series: [{
      name,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: yData,
      lineStyle: { width: 2, color: accent },
      itemStyle: { color: accent, borderColor: '#fff', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: accent + '40' },
          { offset: 1, color: accent + '05' }
        ])
      }
    }]
  }
}

function getPieOptions(data) {
  const accent = getAccentColor()
  const colors = [
    accent,
    '#409eff',
    '#67c23a',
    '#e6a23c',
    '#f56c6c',
    '#909399',
    '#6f7ad3',
    '#58c7da'
  ]
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: { color: 'var(--color-text-secondary)' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: 'var(--color-bg-card)',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: 'var(--color-text-primary)'
        }
      },
      labelLine: { show: false },
      data: data.map((item, idx) => ({
        value: item.count,
        name: item.category,
        itemStyle: { color: colors[idx % colors.length] }
      }))
    }]
  }
}

function initCharts() {
  if (usersChartRef.value) {
    usersChart = echarts.init(usersChartRef.value)
  }
  if (detectionsChartRef.value) {
    detectionsChart = echarts.init(detectionsChartRef.value)
  }
  if (knowledgeChartRef.value) {
    knowledgeChart = echarts.init(knowledgeChartRef.value)
  }
}

async function fetchAllStats() {
  try {
    const [usersTrend, detectionsTrend, knowledgeStats] = await Promise.all([
      getUsersTrend(periodDays.value),
      getDetectionsTrend(periodDays.value),
      getKnowledgeStats()
    ])

    if (usersChart) {
      usersChart.setOption(getLineOptions(
        usersTrend.dates || [],
        usersTrend.counts || [],
        '新增用户'
      ))
    }
    if (detectionsChart) {
      detectionsChart.setOption(getLineOptions(
        detectionsTrend.dates || [],
        detectionsTrend.counts || [],
        '检测量'
      ))
    }
    if (knowledgeChart) {
      knowledgeChart.setOption(getPieOptions(knowledgeStats.by_category || []))
    }
  } catch (e) {
    console.error('获取统计数据失败', e)
  }
}

async function handleExport() {
  try {
    const blob = await exportStats('all', '', '')
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `stats_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

function handleResize() {
  usersChart?.resize()
  detectionsChart?.resize()
  knowledgeChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initCharts()
  await fetchAllStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  usersChart?.dispose()
  detectionsChart?.dispose()
  knowledgeChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.admin-stats {
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

.period-bar {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

.period-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.export-btn {
  margin-left: auto;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  padding: 20px;
  border-radius: 12px;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-container.pie-chart {
  height: 360px;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .period-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .export-btn {
    margin-left: 0;
    width: 100%;
  }
}
</style>
