<template>
  <div class="history-detail-page">
    <div class="detail-container" v-loading="loading">
      <div class="page-header glass-card">
        <div class="header-left">
          <el-button link class="back-btn" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回</span>
          </el-button>
          <div class="header-info">
            <h1 class="page-title ellipsis">{{ detail?.file_name || '检测详情' }}</h1>
            <p class="page-subtitle text-secondary">
              <el-tag :type="detail?.type === 'image' ? 'primary' : 'success'" size="small">
                {{ detail?.type === 'image' ? '图片' : '视频' }}
              </el-tag>
              <span class="create-time">{{ formatDateTime(detail?.created_at) }}</span>
            </p>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="goToKnowledge">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 问诊</span>
          </el-button>
          <el-button type="primary" @click="handleRedetect">
            <el-icon><Refresh /></el-icon>
            <span>重新检测</span>
          </el-button>
          <el-button type="danger" @click="handleDelete">
            <el-icon><Delete /></el-icon>
            <span>删除</span>
          </el-button>
        </div>
      </div>

      <div class="detail-content">
        <div class="left-section">
          <div class="image-section glass-card">
            <h3 class="section-title">检测结果</h3>
            <div class="result-image-wrapper" @click="showImagePreview = true">
              <img
                :src="resultImageUrl"
                :alt="detail?.file_name"
                class="result-image"
              />
              <div class="zoom-hint">
                <el-icon><ZoomIn /></el-icon>
                <span>点击放大</span>
              </div>
            </div>
          </div>

          <div class="stats-section">
            <div class="stat-card glass-card">
              <div class="stat-icon total-icon">
                <el-icon :size="28"><DataAnalysis /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ detail?.detection_count || totalCount }}</p>
                <p class="stat-label">检测总数</p>
              </div>
            </div>
            <div class="stat-card glass-card">
              <div class="stat-icon category-icon">
                <el-icon :size="28"><CollectionTag /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ categoryCount }}</p>
                <p class="stat-label">类别数量</p>
              </div>
            </div>
            <div class="stat-card glass-card">
              <div class="stat-icon time-icon">
                <el-icon :size="28"><Timer /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ formatTime(detail?.inference_time) }}</p>
                <p class="stat-label">检测耗时</p>
              </div>
            </div>
          </div>

          <div v-if="categoryDistribution.length > 0" class="category-section glass-card">
            <h3 class="section-title">类别分布</h3>
            <div class="category-list">
              <div
                v-for="item in categoryDistribution"
                :key="item.name"
                class="category-item"
              >
                <div class="category-info">
                  <span class="category-tag" :style="{ backgroundColor: getCategoryColor(item.name) + '20', color: getCategoryColor(item.name) }">
                    {{ item.name }}
                  </span>
                  <span class="category-count">{{ item.count }} 个</span>
                </div>
                <div class="category-bar">
                  <div
                    class="category-bar-fill"
                    :style="{ width: (item.count / totalCount * 100) + '%', backgroundColor: getCategoryColor(item.name) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="right-section">
          <div class="info-section glass-card">
            <h3 class="section-title">处理信息</h3>
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">模型版本</span>
                <span class="info-value">{{ detail?.model_version || 'YOLOv8' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">检测耗时</span>
                <span class="info-value">{{ formatTime(detail?.inference_time) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">检测时间</span>
                <span class="info-value">{{ formatDateTime(detail?.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">文件大小</span>
                <span class="info-value">{{ formatFileSize(detail?.file_size) }}</span>
              </div>
              <div v-if="detail?.resolution" class="info-item">
                <span class="info-label">分辨率</span>
                <span class="info-value">{{ detail.resolution }}</span>
              </div>
            </div>
          </div>

          <div class="detections-section glass-card">
            <h3 class="section-title">
              检测明细
              <span class="detection-total">共 {{ detail?.detections?.length || 0 }} 条</span>
            </h3>
            <div class="detection-list">
              <div
                v-for="(item, index) in detail?.detections || []"
                :key="index"
                class="detection-item"
              >
                <span class="detection-index">{{ index + 1 }}</span>
                <span class="detection-tag" :style="{ backgroundColor: getCategoryColor(item.class_name || item.category) + '20', color: getCategoryColor(item.class_name || item.category) }">
                  {{ item.class_name || item.category }}
                </span>
                <span class="detection-confidence">
                  置信度: {{ ((item.confidence || 0) * 100).toFixed(1) }}%
                </span>
                <span v-if="item.bbox" class="detection-bbox">
                  [{{ item.bbox.join(', ') }}]
                </span>
              </div>
            </div>
            <div v-if="!detail?.detections?.length" class="empty-detections">
              <el-icon :size="32"><Warning /></el-icon>
              <p>未检测到目标</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-image-viewer
      v-if="showImagePreview"
      :url-list="[resultImageUrl]"
      :initial-index="0"
      @close="showImagePreview = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, ChatDotRound, Refresh, Delete, DataAnalysis,
  CollectionTag, Timer, ZoomIn, Warning
} from '@element-plus/icons-vue'
import { getHistoryDetail, deleteHistory } from '@/api/history'
import { getFullUrl } from '@/utils/format'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const detail = ref(null)
const showImagePreview = ref(false)

const resultImageUrl = computed(() => {
  const img = detail.value?.result_image || detail.value?.image_url
  return img ? getFullUrl(img) : ''
})

const categoryColors = [
  '#E07A5F',
  '#3D9970',
  '#0074D9',
  '#FF851B',
  '#B10DC9',
  '#7FDBFF',
  '#FFDC00',
  '#01FF70',
  '#F012BE',
  '#39CCCC'
]

const colorMap = {}

function getCategoryColor(categoryName) {
  if (!categoryName) return categoryColors[0]
  if (colorMap[categoryName]) {
    return colorMap[categoryName]
  }
  const hash = categoryName.split('').reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc)
  }, 0)
  const color = categoryColors[Math.abs(hash) % categoryColors.length]
  colorMap[categoryName] = color
  return color
}

const totalCount = computed(() => {
  if (detail.value?.detection_count !== undefined) {
    return detail.value.detection_count
  }
  return detail.value?.detections?.length || 0
})

const categoryDistribution = computed(() => {
  if (detail.value?.category_distribution) {
    return Object.entries(detail.value.category_distribution).map(([name, count]) => ({
      name,
      count
    })).sort((a, b) => b.count - a.count)
  }
  if (detail.value?.detections) {
    const distribution = {}
    detail.value.detections.forEach(item => {
      const name = item.class_name || item.category
      if (name) {
        distribution[name] = (distribution[name] || 0) + 1
      }
    })
    return Object.entries(distribution).map(([name, count]) => ({
      name,
      count
    })).sort((a, b) => b.count - a.count)
  }
  return []
})

const categoryCount = computed(() => categoryDistribution.value.length)

onMounted(() => {
  const id = route.params.id
  if (id) {
    loadDetail(id)
  }
})

function formatDateTime(time) {
  if (!time) return '-'
  const date = new Date(time)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

function formatTime(time) {
  if (!time) return '0ms'
  if (time < 1000) {
    return time.toFixed(0) + 'ms'
  }
  return (time / 1000).toFixed(2) + 's'
}

function formatFileSize(size) {
  if (!size) return '-'
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}

async function loadDetail(id) {
  loading.value = true
  try {
    const res = await getHistoryDetail(id)
    detail.value = res.data || {}
  } catch (error) {
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteHistory(route.params.id)
    ElMessage.success('删除成功')
    router.push('/history')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleRedetect() {
  ElMessage.info('重新检测功能开发中...')
}

function goToKnowledge() {
  const detectionContext = encodeURIComponent(JSON.stringify({
    id: detail.value?.id,
    file_name: detail.value?.file_name,
    detections: detail.value?.detections,
    detection_count: totalCount.value,
    category_distribution: categoryDistribution.value
  }))
  router.push({
    path: '/knowledge',
    query: { detection_context: detectionContext }
  })
}
</script>

<style scoped>
.history-detail-page {
  padding: 20px;
  min-height: 100%;
}

.detail-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  gap: 20px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.back-btn {
  flex-shrink: 0;
  padding: 8px;
  font-size: 16px;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.page-subtitle {
  font-size: 13px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.create-time {
  color: var(--color-text-tertiary);
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.detail-content {
  display: flex;
  gap: 20px;
}

.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.right-section {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detection-total {
  font-size: 13px;
  font-weight: 400;
  color: var(--color-text-tertiary);
}

.image-section {
  padding: 20px;
}

.result-image-wrapper {
  position: relative;
  width: 100%;
  max-height: 500px;
  display: flex;
  justify-content: center;
  overflow: hidden;
  border-radius: var(--radius-md);
  cursor: zoom-in;
  background: var(--color-bg-tertiary);
}

.result-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.result-image-wrapper:hover .result-image {
  transform: scale(1.02);
}

.zoom-hint {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 20px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.result-image-wrapper:hover .zoom-hint {
  opacity: 1;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.total-icon {
  background: rgba(224, 122, 95, 0.15);
  color: #E07A5F;
}

.category-icon {
  background: rgba(61, 153, 112, 0.15);
  color: #3D9970;
}

.time-icon {
  background: rgba(0, 116, 217, 0.15);
  color: #0074D9;
}

[data-theme="dark"] .total-icon {
  background: rgba(224, 122, 95, 0.1);
}

[data-theme="dark"] .category-icon {
  background: rgba(61, 153, 112, 0.1);
}

[data-theme="dark"] .time-icon {
  background: rgba(0, 116, 217, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 4px 0 0 0;
}

.category-section {
  padding: 20px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.category-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.category-count {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.category-bar {
  height: 6px;
  background: var(--color-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.category-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.info-section {
  padding: 20px;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border-light);
}

.info-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.detections-section {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.detection-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 500px;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  transition: background 0.2s ease;
  flex-wrap: wrap;
}

.detection-item:hover {
  background: var(--color-bg-tertiary);
}

.detection-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-accent-glow);
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detection-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}

.detection-confidence {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.detection-bbox {
  font-size: 12px;
  color: var(--color-text-tertiary);
  font-family: var(--font-family-mono);
  margin-left: auto;
}

.empty-detections {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--color-text-tertiary);
  gap: 12px;
}

@media (max-width: 1200px) {
  .detail-content {
    flex-direction: column;
  }

  .right-section {
    width: 100%;
  }

  .detection-list {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .history-detail-page {
    padding: 12px;
  }

  .detail-container {
    gap: 12px;
  }

  .page-header {
    padding: 16px;
    flex-direction: column;
    align-items: stretch;
  }

  .header-left {
    gap: 12px;
  }

  .page-title {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .image-section,
  .category-section,
  .info-section,
  .detections-section {
    padding: 16px;
  }

  .detection-bbox {
    display: none;
  }
}

@media (max-width: 480px) {
  .history-detail-page {
    padding: 8px;
  }

  .page-header {
    padding: 12px;
  }

  .page-title {
    font-size: 16px;
  }

  .section-title {
    font-size: 16px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 20px;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .header-actions .el-button {
    flex: 1 1 100%;
  }
}
</style>
