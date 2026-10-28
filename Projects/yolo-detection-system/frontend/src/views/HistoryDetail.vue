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
            <h1 class="page-title ellipsis">{{ detail?.original_filename || '检测详情' }}</h1>
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
          <el-button :loading="shareLoading" @click="handleShare">
            <el-icon><Share /></el-icon>
            <span>分享</span>
          </el-button>
          <el-button :loading="exportLoading" @click="handleExportReport">
            <el-icon><Document /></el-icon>
            <span>导出报告</span>
          </el-button>
          <el-button :loading="pdfLoading" @click="handleDownloadPdf">
            <el-icon><Download /></el-icon>
            <span>下载 PDF</span>
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
            <div v-if="detail?.type === 'video'" class="video-migration-hint">
              <el-icon :size="48"><VideoCamera /></el-icon>
              <p class="hint-title">视频检测功能已移至移动端App</p>
              <p class="hint-desc">该检测记录来自旧版本视频检测功能，网页端已不再支持视频检测。请下载移动端App体验视频检测功能。</p>
            </div>
            <div v-else class="result-image-wrapper" @click="showImagePreview = true">
              <img
                :src="resultImageUrl"
                :alt="detail?.original_filename"
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
                <p class="stat-value">{{ formatTime(detail?.processing_time) }}</p>
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
                <span class="info-value">{{ formatTime(detail?.processing_time) }}</span>
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
              <span class="detection-total">共 {{ detections.length }} 条</span>
            </h3>
            <el-alert
              v-if="lowConfidence"
              type="warning"
              show-icon
              :closable="false"
              class="low-confidence-alert"
            >
              <template #title>
                检测置信度偏低（阈值 {{ formatThreshold(lowConfidence.threshold) }}），建议重新拍摄清晰叶片照片
              </template>
              <div class="low-confidence-detail">
                <div v-if="lowConfidence.candidates.length" class="candidate-line">
                  <span class="candidate-label">可能：</span>
                  <el-tag
                    v-for="candidate in lowConfidence.candidates"
                    :key="candidate.class_id ?? candidate.class_name"
                    type="warning"
                    effect="plain"
                    size="small"
                    class="candidate-tag"
                  >{{ candidate.class_name }}({{ formatConfidencePercent(candidate.confidence) }}%)</el-tag>
                </div>
                <p v-if="lowConfidence.samplePoolId" class="sample-pool-note">该图片已自动收录至样本池待人工复核</p>
              </div>
            </el-alert>
            <div class="detection-list">
              <div
                v-for="(item, index) in detections"
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
            <div v-if="detections.length === 0" class="empty-detections">
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

    <el-dialog
      v-model="shareVisible"
      title="分享检测结果"
      width="420px"
      class="share-dialog"
      append-to-body
    >
      <div v-loading="shareLoading" class="share-content">
        <div v-if="shareError" class="share-error">
          <el-icon><Warning /></el-icon>
          <span>{{ shareError }}</span>
        </div>
        <template v-else-if="shareData">
          <img
            v-if="shareData.qr_code"
            :src="'data:image/png;base64,' + shareData.qr_code"
            alt="分享二维码"
            class="share-qr"
          />
          <p v-else class="share-qr-missing">二维码生成失败，可复制链接分享</p>
          <div class="share-link-row">
            <el-input :model-value="shareData.share_url" readonly />
            <el-button type="primary" @click="copyShareLink">复制链接</el-button>
          </div>
          <p class="share-expire">{{ shareExpireText }}</p>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, ChatDotRound, Refresh, Delete, DataAnalysis,
  CollectionTag, Timer, ZoomIn, Warning, VideoCamera, Document, Download, Share
} from '@element-plus/icons-vue'
import { getHistoryDetail, deleteHistory, getHistoryReport, downloadHistoryReportPdf, shareHistory } from '@/api/history'
import { getFullUrl } from '@/utils/format'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const detail = ref(null)
const showImagePreview = ref(false)
const exportLoading = ref(false)
const pdfLoading = ref(false)
const shareVisible = ref(false)
const shareLoading = ref(false)
const shareError = ref('')
const shareData = ref(null)

const resultImageUrl = computed(() => {
  const img = detail.value?.result_path || detail.value?.original_path
  return img ? getFullUrl(img) : ''
})

const detectionResult = computed(() => detail.value?.detection_result || {})

const detections = computed(() => detectionResult.value.detections || [])

function deriveCandidates(list) {
  const best = {}
  list.forEach((item) => {
    const confidence = item?.confidence
    if (item?.class_id == null || typeof confidence !== 'number') return
    if (!best[item.class_id] || confidence > best[item.class_id].confidence) {
      best[item.class_id] = {
        class_id: item.class_id,
        class_name: item.class_name || item.category,
        confidence
      }
    }
  })
  return Object.values(best).sort((a, b) => b.confidence - a.confidence).slice(0, 3)
}

const lowConfidence = computed(() => {
  const result = detectionResult.value
  const threshold = typeof result.confidence_threshold === 'number'
    ? result.confidence_threshold
    : (typeof detail.value?.confidence_threshold === 'number' ? detail.value.confidence_threshold : 0.5)
  let isLow = result.low_confidence === true || detail.value?.low_confidence === true
  if (result.low_confidence === undefined && detail.value?.low_confidence === undefined) {
    const maxConfidence = detail.value?.max_confidence
    isLow = typeof maxConfidence === 'number' && maxConfidence < threshold
  }
  if (!isLow) return null
  const candidates = Array.isArray(result.top_candidates)
    ? result.top_candidates
    : deriveCandidates(detections.value)
  return {
    threshold,
    candidates: candidates.filter((item) => item && item.class_name),
    samplePoolId: result.sample_pool_id ?? detail.value?.sample_pool_id ?? null
  }
})

function formatThreshold(value) {
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : '-'
}

function formatConfidencePercent(value) {
  return typeof value === 'number' ? Math.round(value * 100) : 0
}

const categoryColors = [
  '#C8442F',
  '#3A7D55',
  '#4E7A6D',
  '#D9A11E',
  '#A6694F',
  '#5B665F',
  '#8A938C',
  '#C73E2D',
  '#335B46',
  '#7A8B5C'
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
  if (detail.value?.detection_count !== undefined && detail.value?.detection_count !== null) {
    return detail.value.detection_count
  }
  if (detectionResult.value.total_count !== undefined) {
    return detectionResult.value.total_count
  }
  return detections.value.length
})

const categoryDistribution = computed(() => {
  const summary = detectionResult.value.class_summary
  if (summary) {
    return Object.entries(summary).map(([name, count]) => ({
      name,
      count
    })).sort((a, b) => b.count - a.count)
  }
  const distribution = {}
  detections.value.forEach(item => {
    const name = item.class_name || item.category
    if (name) {
      distribution[name] = (distribution[name] || 0) + 1
    }
  })
  return Object.entries(distribution).map(([name, count]) => ({
    name,
    count
  })).sort((a, b) => b.count - a.count)
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

function formatTime(seconds) {
  if (!seconds && seconds !== 0) return '-'
  if (seconds < 1) {
    return (seconds * 1000).toFixed(0) + 'ms'
  }
  return seconds.toFixed(2) + 's'
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
    detail.value = res || {}
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

async function handleExportReport() {
  const id = route.params.id
  if (!id) return
  exportLoading.value = true
  try {
    const res = await getHistoryReport(id)
    const html = await res.data.text()
    const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:5000'
    const processedHtml = html.replace(/src="\/static\//g, `src="${baseUrl}/static/`)
    const blob = new Blob([processedHtml], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const win = window.open(url, '_blank')
    if (!win) {
      ElMessage.warning('请允许浏览器弹出窗口后再试')
      return
    }
  } catch (error) {
    console.error('导出报告失败', error)
  } finally {
    exportLoading.value = false
  }
}

async function handleDownloadPdf() {
  const id = route.params.id
  if (!id) return
  pdfLoading.value = true
  try {
    const res = await downloadHistoryReportPdf(id)
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `detection_report_${id}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('PDF 报告下载成功')
  } catch (error) {
    console.error('下载 PDF 失败', error)
    ElMessage.error('下载 PDF 失败，请稍后重试')
  } finally {
    pdfLoading.value = false
  }
}

async function handleShare() {
  const id = route.params.id
  if (!id) return
  shareVisible.value = true
  shareLoading.value = true
  shareError.value = ''
  shareData.value = null
  try {
    shareData.value = await shareHistory(id)
  } catch (error) {
    shareError.value = error?.response?.data?.message || '分享链接生成失败，请稍后重试'
  } finally {
    shareLoading.value = false
  }
}

const shareExpireText = computed(() => {
  const expiresAt = shareData.value?.expires_at
  if (!expiresAt) return ''
  const expireTime = new Date(expiresAt).getTime()
  if (Number.isNaN(expireTime)) return ''
  const days = Math.ceil((expireTime - Date.now()) / (24 * 60 * 60 * 1000))
  return days > 0 ? `${days} 天后失效` : '分享链接已失效'
})

function fallbackCopy(text) {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  document.body.removeChild(textarea)
  if (!copied) throw new Error('copy failed')
}

async function copyShareLink() {
  const link = shareData.value?.share_url
  if (!link) return
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(link)
    } else {
      fallbackCopy(link)
    }
    ElMessage.success('链接已复制')
  } catch (error) {
    try {
      fallbackCopy(link)
      ElMessage.success('链接已复制')
    } catch (fallbackError) {
      ElMessage.warning('复制失败，请手动复制链接')
    }
  }
}

function goToKnowledge() {
  const diseaseItems = detections.value.filter(d => d.class_name !== '健康叶片')
  const topDisease = diseaseItems
    .slice()
    .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))[0] || null
  const context = {
    id: detail.value?.id,
    file_name: detail.value?.original_filename,
    detections: detections.value,
    detection_count: totalCount.value,
    category_distribution: categoryDistribution.value
  }
  if (topDisease) {
    context.detected_class_id = topDisease.class_id
  }
  const detectionContext = encodeURIComponent(JSON.stringify(context))
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
  flex-wrap: wrap;
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

.low-confidence-alert {
  margin-bottom: 16px;
}

.low-confidence-detail {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.candidate-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.candidate-label {
  font-weight: 500;
}

.candidate-tag {
  margin: 0;
}

.sample-pool-note {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.share-content {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.share-qr {
  width: 200px;
  height: 200px;
  object-fit: contain;
  border-radius: var(--radius-md);
  background: #fff;
  padding: 8px;
}

.share-qr-missing {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.share-link-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.share-link-row .el-input {
  flex: 1;
}

.share-expire {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.share-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(199, 62, 45, 0.1);
  color: var(--color-error);
  font-size: 13px;
}

.image-section {
  padding: 20px;
}

.video-migration-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--color-text-secondary);
}

.video-migration-hint .el-icon {
  color: var(--color-accent);
  margin-bottom: 16px;
}

.hint-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.hint-desc {
  font-size: 14px;
  color: var(--color-text-tertiary);
  margin: 0;
  max-width: 400px;
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
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.category-icon {
  background: var(--color-forest-soft);
  color: var(--color-forest);
}

.time-icon {
  background: rgba(78, 122, 109, 0.12);
  color: var(--color-info);
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
