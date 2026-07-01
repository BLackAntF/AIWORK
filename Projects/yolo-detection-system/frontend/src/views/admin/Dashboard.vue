<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <h2 class="page-title">管理概览</h2>
      <p class="page-subtitle">实时掌握系统运行状态</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card glass-card glow-border">
        <div class="stat-icon users-icon">
          <el-icon :size="28"><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ dashboardData.users?.total || 0 }}</div>
          <div class="stat-label">用户总数</div>
          <div class="stat-trend">
            <el-icon class="trend-icon up"><TrendCharts /></el-icon>
            <span>今日新增 {{ dashboardData.users?.new_today || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card glass-card glow-border">
        <div class="stat-icon detections-icon">
          <el-icon :size="28"><Search /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ dashboardData.detections?.total || 0 }}</div>
          <div class="stat-label">检测总数</div>
          <div class="stat-trend">
            <el-icon class="trend-icon up"><TrendCharts /></el-icon>
            <span>今日检测 {{ dashboardData.detections?.today || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card glass-card glow-border">
        <div class="stat-icon knowledge-icon">
          <el-icon :size="28"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ dashboardData.knowledge?.total || 0 }}</div>
          <div class="stat-label">知识库条数</div>
          <div class="stat-trend">
            <el-icon class="trend-icon"><Folder /></el-icon>
            <span>{{ dashboardData.knowledge?.categories || 0 }} 个分类</span>
          </div>
        </div>
      </div>

      <div class="stat-card glass-card glow-border">
        <div class="stat-icon chats-icon">
          <el-icon :size="28"><ChatDotRound /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ dashboardData.chats?.total || 0 }}</div>
          <div class="stat-label">今日对话数</div>
          <div class="stat-trend">
            <el-icon class="trend-icon up"><TrendCharts /></el-icon>
            <span>今日 {{ dashboardData.chats?.today || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h3 class="section-title">快捷入口</h3>
      <div class="action-cards">
        <div class="action-card glass-card" @click="goTo('/admin/users')">
          <el-icon :size="32" class="action-icon"><User /></el-icon>
          <span class="action-text">用户管理</span>
        </div>
        <div class="action-card glass-card" @click="goTo('/admin/knowledge')">
          <el-icon :size="32" class="action-icon"><Document /></el-icon>
          <span class="action-text">知识库管理</span>
        </div>
        <div class="action-card glass-card" @click="goTo('/admin/detections')">
          <el-icon :size="32" class="action-icon"><Search /></el-icon>
          <span class="action-text">检测记录</span>
        </div>
        <div class="action-card glass-card" @click="goTo('/admin/stats')">
          <el-icon :size="32" class="action-icon"><DataLine /></el-icon>
          <span class="action-text">数据统计</span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card glass-card">
        <div class="chart-header">
          <h3 class="chart-title">用户增长趋势</h3>
          <el-select v-model="trendDays" size="small" @change="fetchTrends" style="width: 120px">
            <el-option label="近7天" :value="7" />
            <el-option label="近30天" :value="30" />
          </el-select>
        </div>
        <div ref="usersChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card glass-card">
        <div class="chart-header">
          <h3 class="chart-title">检测量趋势</h3>
          <el-select v-model="trendDays" size="small" @change="fetchTrends" style="width: 120px">
            <el-option label="近7天" :value="7" />
            <el-option label="近30天" :value="30" />
          </el-select>
        </div>
        <div ref="detectionsChartRef" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  User, Search, Document, ChatDotRound, TrendCharts, Folder, DataLine
} from '@element-plus/icons-vue'
import {
  getDashboardStats, getUsersTrend, getDetectionsTrend
} from '@/api/admin'

const router = useRouter()
const dashboardData = ref({})
const trendDays = ref(7)
const usersChartRef = ref(null)
const detectionsChartRef = ref(null)
let usersChart = null
let detectionsChart = null

function goTo(path) {
  router.push(path)
}

function getChartOptions(xData, yData, title, color) {
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
      name: title,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: yData,
      lineStyle: { width: 2, color: color },
      itemStyle: { color: color, borderColor: '#fff', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: color + '40' },
          { offset: 1, color: color + '05' }
        ])
      }
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
}

function updateCharts(usersData, detectionsData) {
  const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim()

  if (usersChart) {
    usersChart.setOption(getChartOptions(
      usersData.dates || [],
      usersData.counts || [],
      '用户增长',
      accentColor
    ))
  }
  if (detectionsChart) {
    detectionsChart.setOption(getChartOptions(
      detectionsData.dates || [],
      detectionsData.counts || [],
      '检测量',
      accentColor
    ))
  }
}

async function fetchDashboard() {
  try {
    dashboardData.value = await getDashboardStats()
  } catch (e) {
    dashboardData.value = {
      users: { total: 0, new_today: 0 },
      detections: { total: 0, today: 0 },
      knowledge: { total: 0, categories: 0 },
      chats: { total: 0, today: 0 }
    }
  }
}

async function fetchTrends() {
  try {
    const [usersTrend, detectionsTrend] = await Promise.all([
      getUsersTrend(trendDays.value),
      getDetectionsTrend(trendDays.value)
    ])
    updateCharts(usersTrend, detectionsTrend)
  } catch (e) {
    updateCharts(
      { dates: [], counts: [] },
      { dates: [], counts: [] }
    )
  }
}

function handleResize() {
  usersChart?.resize()
  detectionsChart?.resize()
}

onMounted(async () => {
  await fetchDashboard()
  await nextTick()
  initCharts()
  await fetchTrends()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  usersChart?.dispose()
  detectionsChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.users-icon {
  background: rgba(64, 158, 255, 0.15);
  color: #409eff;
}

.detections-icon {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}

.knowledge-icon {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
}

.chats-icon {
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
  font-family: var(--font-mono);
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 6px;
}

.trend-icon.up {
  color: #67c23a;
}

.quick-actions {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px 0;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-accent);
}

.action-icon {
  color: var(--color-accent);
}

.action-text {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
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

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  height: 300px;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .action-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .action-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .action-card {
    padding: 16px;
  }
  .stat-value {
    font-size: 24px;
  }
}
</style>
