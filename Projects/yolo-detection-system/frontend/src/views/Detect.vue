<template>
  <div class="detect-page">
    <div class="page-header">
      <h1 class="page-title">智能目标检测</h1>
      <p class="page-subtitle">上传图片，AI 快速识别目标</p>
    </div>

    <div class="detect-container">
      <div class="left-panel">
        <div class="upload-section glass-card">
          <div
            class="upload-area"
            :class="{ 'drag-over': isDragOver, 'has-file': imageFiles.length > 0 }"
            @click="triggerImageUpload"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleImageDrop"
          >
            <input
              ref="imageInput"
              type="file"
              multiple
              accept="image/jpeg,image/png,image/bmp,image/webp"
              class="file-input"
              @change="handleImageChange"
              hidden
            />
            <div v-if="imageFiles.length === 0" class="upload-placeholder">
              <el-icon :size="56" class="upload-icon"><Picture /></el-icon>
              <p class="upload-text">点击或拖拽图片到此处上传</p>
              <p class="upload-tip">支持 JPG、PNG、BMP、WEBP 格式，可多选批量检测</p>
              <p class="upload-info">单张图片不超过 10MB，单次最多 20 张</p>
            </div>
            <div v-else class="preview-grid">
              <div
                v-for="(item, index) in imageFiles"
                :key="index"
                class="preview-item"
              >
                <img
                  :src="item.preview"
                  :alt="item.file.name"
                  class="preview-thumb"
                  @click.stop="handlePreviewImage(item.preview)"
                />
                <button class="remove-btn" @click.stop="removeImage(index)">
                  <el-icon><Close /></el-icon>
                </button>
              </div>
              <div class="preview-add" @click.stop="triggerImageUpload">
                <el-icon :size="28"><Plus /></el-icon>
                <span>添加图片</span>
              </div>
            </div>
          </div>

          <div class="upload-actions">
            <div class="save-history">
              <el-switch v-model="saveHistory" />
              <span class="save-history-text">保存到历史记录</span>
            </div>
            <el-button
              type="primary"
              class="detect-btn glow-border"
              :disabled="!canDetect || isDetecting"
              :loading="isDetecting"
              @click="handleDetect"
            >
              <el-icon><Search /></el-icon>
              <span>{{ detectButtonText }}</span>
            </el-button>
          </div>
        </div>

        <div v-if="detectionResult" class="result-section glass-card slide-up">
          <div class="result-header">
            <h3 class="section-title">检测结果</h3>
            <el-button text type="primary" @click="handlePreviewResult">
              <el-icon><ZoomIn /></el-icon>
              <span>放大查看</span>
            </el-button>
          </div>
          <div class="result-image-wrapper">
            <img :src="resultImageUrl" alt="检测结果" class="result-image" @click="handlePreviewResult" />
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div v-if="isDetecting" class="detecting-section glass-card">
          <div class="detecting-animation">
            <div class="scan-line"></div>
            <el-icon :size="64" class="detecting-icon"><Loading /></el-icon>
          </div>
          <h3 class="detecting-title">AI 正在分析中</h3>
          <p class="detecting-text">请稍候，正在识别目标...</p>
          <el-progress :percentage="detectProgress" :stroke-width="6" :show-text="false" class="detect-progress" />
          <el-button v-if="!isCanceling" text type="danger" @click="handleCancel">取消检测</el-button>
        </div>

        <div v-else-if="detectionResult" class="stats-section slide-up">
          <div class="stat-cards">
            <div class="stat-card glass-card hover-lift">
              <div class="stat-icon total-icon">
                <el-icon :size="28"><DataAnalysis /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ detectionResult.total_count }}</p>
                <p class="stat-label">检测目标总数</p>
              </div>
            </div>
            <div class="stat-card glass-card hover-lift">
              <div class="stat-icon time-icon">
                <el-icon :size="28"><Timer /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ formatProcessingTime(detectionResult.processing_time) }}</p>
                <p class="stat-label">处理耗时</p>
              </div>
            </div>
            <div class="stat-card glass-card hover-lift">
              <div class="stat-icon model-icon">
                <el-icon :size="28"><Cpu /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value model-version">{{ detectionResult.model_version }}</p>
                <p class="stat-label">模型版本</p>
              </div>
            </div>
          </div>

          <div v-if="classSummaryList.length > 0" class="category-section glass-card">
            <h3 class="section-title">类别分布</h3>
            <div class="category-list">
              <div
                v-for="item in classSummaryList"
                :key="item.name"
                class="category-item"
              >
                <div class="category-info">
                  <span
                    class="category-tag"
                    :style="{ backgroundColor: getCategoryColor(item.name) + '20', color: getCategoryColor(item.name) }"
                  >
                    {{ item.name }}
                  </span>
                  <span class="category-count">{{ item.count }} 个</span>
                </div>
                <div class="category-bar">
                  <div
                    class="category-bar-fill"
                    :style="{ width: (item.count / detectionResult.total_count * 100) + '%', backgroundColor: getCategoryColor(item.name) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="detectionResult.detections?.length > 0" class="detections-section glass-card">
            <h3 class="section-title">检测结果列表</h3>
            <div class="detection-list">
              <div
                v-for="(item, index) in detectionResult.detections"
                :key="index"
                class="detection-item"
              >
                <div class="detection-header">
                  <span class="detection-index">{{ index + 1 }}</span>
                  <span
                    class="detection-tag"
                    :style="{ backgroundColor: getCategoryColor(item.class_name) + '20', color: getCategoryColor(item.class_name) }"
                  >
                    {{ item.class_name }}
                  </span>
                  <span class="detection-confidence-text">{{ (item.confidence * 100).toFixed(1) }}%</span>
                </div>
                <div class="detection-confidence-bar">
                  <div
                    class="confidence-fill"
                    :style="{ width: (item.confidence * 100) + '%', backgroundColor: getCategoryColor(item.class_name) }"
                  ></div>
                </div>
                <div class="detection-bbox">
                  <el-icon><Position /></el-icon>
                  <span>坐标: [{{ item.bbox?.join(', ') || '-' }}]</span>
                </div>

                <div v-if="item.disease_profile && item.class_name !== '健康叶片'" class="disease-profile-section">
                  <div class="profile-header">
                    <el-icon><Document /></el-icon>
                    <span>病害档案</span>
                    <el-tag type="warning" effect="light" size="small">{{ item.disease_profile.disease_name }}</el-tag>
                  </div>
                  <div class="profile-content">
                    <div class="profile-item">
                      <span class="profile-label">诱因</span>
                      <span class="profile-value">{{ item.disease_profile.causes }}</span>
                    </div>
                    <div class="profile-item">
                      <span class="profile-label">典型症状</span>
                      <span class="profile-value">{{ item.disease_profile.symptoms }}</span>
                    </div>
                    <div class="profile-item" v-if="item.disease_profile.occurrence">
                      <span class="profile-label">发生规律</span>
                      <span class="profile-value">{{ item.disease_profile.occurrence }}</span>
                    </div>
                    <div class="profile-item">
                      <span class="profile-label">预防措施</span>
                      <span class="profile-value">{{ item.disease_profile.prevention }}</span>
                    </div>
                    <div class="profile-item">
                      <span class="profile-label">治疗方案</span>
                      <span class="profile-value">{{ item.disease_profile.treatment }}</span>
                    </div>
                    <div class="profile-item">
                      <span class="profile-label">推荐药剂</span>
                      <span class="profile-value">{{ item.disease_profile.pesticides }}</span>
                    </div>
                  </div>
                  <div class="profile-actions">
                    <el-button type="primary" class="ask-btn" @click="askAboutDisease(item)">
                      <el-icon><ChatDotRound /></el-icon>
                      咨询此病害
                    </el-button>
                    <el-button type="success" class="ask-btn" @click="askTreatmentPlan(item)">
                      <el-icon><MagicStick /></el-icon>
                      防治方案直达
                    </el-button>
                  </div>
                </div>

                <div v-else-if="item.class_name === '健康叶片'" class="healthy-section">
                  <el-tag type="success" effect="light" size="large">
                    <el-icon><CircleCheck /></el-icon>
                    健康叶片
                  </el-tag>
                  <p class="healthy-hint">该叶片未检测到病害特征，继续保持良好管理。</p>
                </div>
              </div>
            </div>
          </div>

          <div class="action-buttons">
            <el-button class="action-btn ai-btn glow-border" @click="handleAiConsult">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI 问诊</span>
            </el-button>
            <el-button class="action-btn" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              <span>重新检测</span>
            </el-button>
            <el-button class="action-btn" @click="handleDownload">
              <el-icon><Download /></el-icon>
              <span>下载结果</span>
            </el-button>
          </div>
        </div>

        <div v-else-if="batchResult" class="stats-section slide-up">
          <div class="stat-cards">
            <div class="stat-card glass-card hover-lift">
              <div class="stat-icon total-icon">
                <el-icon :size="28"><CircleCheck /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ batchResult.success_count }}</p>
                <p class="stat-label">检测成功</p>
              </div>
            </div>
            <div class="stat-card glass-card hover-lift">
              <div class="stat-icon time-icon">
                <el-icon :size="28"><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ batchResult.failed_count }}</p>
                <p class="stat-label">检测失败</p>
              </div>
            </div>
            <div class="stat-card glass-card hover-lift">
              <div class="stat-icon model-icon">
                <el-icon :size="28"><DataAnalysis /></el-icon>
              </div>
              <div class="stat-content">
                <p class="stat-value">{{ batchTotalCount }}</p>
                <p class="stat-label">检出目标总数</p>
              </div>
            </div>
          </div>

          <div class="batch-section glass-card">
            <h3 class="section-title">批量检测结果</h3>
            <el-table :data="batchRows" size="small" max-height="420" class="batch-table">
              <el-table-column label="结果图" width="76">
                <template #default="{ row }">
                  <img
                    v-if="row.result_image"
                    :src="getFullUrl(row.result_image)"
                    :alt="row.original_filename"
                    class="batch-thumb"
                    @click="handlePreviewImage(getFullUrl(row.result_image))"
                  />
                  <span v-else class="text-placeholder">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="original_filename" label="文件名" min-width="150" show-overflow-tooltip />
              <el-table-column label="检出病害" min-width="150">
                <template #default="{ row }">
                  <span>{{ formatClassSummary(row.class_summary) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="检出数" width="80">
                <template #default="{ row }">
                  <span>{{ row.total_count ?? '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="耗时" width="90">
                <template #default="{ row }">
                  <span>{{ row.success ? formatProcessingTime(row.processing_time) : '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="90">
                <template #default="{ row }">
                  <el-tooltip v-if="!row.success" :content="row.error || '检测失败'" placement="top">
                    <el-tag type="danger" size="small">失败</el-tag>
                  </el-tooltip>
                  <el-tag v-else type="success" size="small">成功</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="action-buttons batch-actions">
            <el-button class="action-btn ai-btn glow-border" @click="handleBatchAiConsult">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI 问诊</span>
            </el-button>
            <el-button class="action-btn" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              <span>清空结果</span>
            </el-button>
          </div>
        </div>

        <div v-else class="empty-section glass-card">
          <el-icon :size="64" class="empty-icon"><Monitor /></el-icon>
          <h3 class="empty-title">等待检测</h3>
          <p class="empty-text">上传图片后点击开始检测</p>
        </div>
      </div>
    </div>

    <el-dialog v-model="previewVisible" width="80%" class="preview-dialog">
      <img :src="previewImageUrl" alt="预览" class="dialog-preview-image" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Picture,
  Close,
  Search,
  Loading,
  DataAnalysis,
  Timer,
  Cpu,
  Position,
  ChatDotRound,
  Refresh,
  Download,
  Monitor,
  ZoomIn,
  Document,
  CircleCheck,
  MagicStick,
  Plus,
  Warning
} from '@element-plus/icons-vue'
import { detectImage, detectBatch } from '@/api/detection'
import { useChatStore } from '@/store/modules/chat'
import { getFullUrl } from '@/utils/format'

const router = useRouter()
const chatStore = useChatStore()

// 与后端 config.MAX_BATCH_IMAGES 保持一致
const MAX_BATCH_IMAGES = 20
const MAX_FILE_SIZE = 10 * 1024 * 1024

const saveHistory = ref(true)
const isDetecting = ref(false)
const isCanceling = ref(false)
const detectProgress = ref(0)
const detectionResult = ref(null)
const batchResult = ref(null)
const batchRows = ref([])
const previewVisible = ref(false)
const previewImageUrl = ref('')

const imageInput = ref(null)
const imageFiles = ref([])
const isDragOver = ref(false)

let progressTimer = null

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

const canDetect = computed(() => {
  return imageFiles.value.length > 0
})

const detectButtonText = computed(() => {
  if (isDetecting.value) return '检测中...'
  if (imageFiles.value.length > 1) return `开始批量检测 (${imageFiles.value.length})`
  return '开始检测'
})

const batchTotalCount = computed(() => {
  return batchRows.value.reduce((sum, row) => sum + (row.total_count || 0), 0)
})

const batchClassSummary = computed(() => {
  const merged = {}
  batchRows.value.forEach((row) => {
    if (!row.success || !row.class_summary) return
    Object.entries(row.class_summary).forEach(([name, count]) => {
      merged[name] = (merged[name] || 0) + count
    })
  })
  return merged
})

const resultImageUrl = computed(() => {
  if (!detectionResult.value?.result_image) return ''
  return getFullUrl(detectionResult.value.result_image)
})

const classSummaryList = computed(() => {
  if (!detectionResult.value?.class_summary) return []
  return Object.entries(detectionResult.value.class_summary)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

function formatProcessingTime(time) {
  if (!time && time !== 0) return '-'
  if (time < 1) {
    return (time * 1000).toFixed(0) + 'ms'
  }
  return time.toFixed(3) + 's'
}

function triggerImageUpload() {
  imageInput.value?.click()
}

function handleDragOver() {
  isDragOver.value = true
}

function handleDragLeave() {
  isDragOver.value = false
}

function validateImageFile(file) {
  const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.error(`${file.name}：仅支持 JPG、PNG、BMP 或 WEBP 格式`)
    return false
  }
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.error(`${file.name}：图片大小不能超过 10MB`)
    return false
  }
  return true
}

function addFiles(fileList) {
  const incoming = Array.from(fileList || []).filter(validateImageFile)
  if (incoming.length === 0) return

  const remain = MAX_BATCH_IMAGES - imageFiles.value.length
  if (remain <= 0) {
    ElMessage.warning(`单次最多上传 ${MAX_BATCH_IMAGES} 张图片`)
    return
  }
  if (incoming.length > remain) {
    ElMessage.warning(`单次最多上传 ${MAX_BATCH_IMAGES} 张图片，已保留前 ${remain} 张`)
  }

  incoming.slice(0, remain).forEach((file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      imageFiles.value.push({ file, preview: e.target?.result })
    }
    reader.readAsDataURL(file)
  })

  resetResults()
}

function resetResults() {
  detectionResult.value = null
  batchResult.value = null
  batchRows.value = []
}

function handleImageChange(e) {
  addFiles(e.target.files)
  e.target.value = ''
}

function handleImageDrop(e) {
  isDragOver.value = false
  addFiles(e.dataTransfer.files)
}

function removeImage(index) {
  imageFiles.value.splice(index, 1)
  resetResults()
}

function startProgressSimulation() {
  detectProgress.value = 0
  progressTimer = setInterval(() => {
    if (detectProgress.value < 90) {
      detectProgress.value += Math.random() * 8
      if (detectProgress.value > 90) detectProgress.value = 90
    }
  }, 300)
}

function stopProgressSimulation() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  detectProgress.value = 100
}

async function handleDetect() {
  if (!canDetect.value) return

  isDetecting.value = true
  isCanceling.value = false
  resetResults()
  startProgressSimulation()

  try {
    if (imageFiles.value.length > 1) {
      const res = await detectBatch(imageFiles.value.map(item => item.file), saveHistory.value)
      batchResult.value = res
      batchRows.value = res.list || []
      stopProgressSimulation()
      ElMessage.success(`批量检测完成：成功 ${res.success_count} 张，失败 ${res.failed_count} 张`)
    } else {
      const result = await detectImage(imageFiles.value[0].file, saveHistory.value)
      detectionResult.value = result
      stopProgressSimulation()
      ElMessage.success('检测完成')
    }
  } catch (error) {
    stopProgressSimulation()
    if (!isCanceling.value) {
      ElMessage.error(error.message || '检测失败，请重试')
    }
  } finally {
    isDetecting.value = false
    isCanceling.value = false
  }
}

function handleCancel() {
  ElMessageBox.confirm(
    '请求已发送至服务器，取消仅关闭当前页面提示，服务器端检测仍将继续执行。确定要取消吗？',
    '取消检测',
    {
      confirmButtonText: '确定取消',
      cancelButtonText: '继续等待',
      type: 'warning'
    }
  ).then(() => {
    isCanceling.value = true
    stopProgressSimulation()
    isDetecting.value = false
    ElMessage.info('已取消（服务器端仍在执行，完成后结果将保存在历史记录中）')
  }).catch(() => {})
}

function handlePreviewImage(url) {
  if (!url) return
  previewImageUrl.value = url
  previewVisible.value = true
}

function formatClassSummary(summary) {
  if (!summary) return '-'
  const parts = Object.entries(summary).map(([name, count]) => `${name}×${count}`)
  return parts.length > 0 ? parts.join('、') : '-'
}

function handlePreviewResult() {
  if (resultImageUrl.value) {
    previewImageUrl.value = resultImageUrl.value
    previewVisible.value = true
  }
}

function handleAiConsult() {
  if (!detectionResult.value) {
    ElMessage.warning('请先完成检测')
    return
  }
  chatStore.setDetectionResult(detectionResult.value)
  const detections = detectionResult.value.detections || []
  const diseaseItems = detections.filter(d => d.class_name !== '健康叶片')
  const firstDisease = diseaseItems[0] || null
  chatStore.setDetectionContext({
    class_id: firstDisease?.class_id ?? null,
    disease_name: firstDisease?.disease_profile?.disease_name || firstDisease?.class_name || '',
    detection_context: `本次检测共检出 ${detectionResult.value.detection_count ?? detections.length} 个目标，`
      + `病害分布：${formatClassSummary(detectionResult.value.class_summary)}`
  })
  const resultData = encodeURIComponent(JSON.stringify(detectionResult.value))
  router.push({
    path: '/knowledge',
    query: { result: resultData }
  })
}

function askAboutDisease(item) {
  chatStore.setDetectionContext({
    class_id: item.class_id,
    disease_name: item.disease_profile?.disease_name || item.class_name,
    detection_context: `${item.class_name} (${(item.confidence * 100).toFixed(1)}%)`
  })
  router.push('/knowledge')
}

function askTreatmentPlan(item) {
  const diseaseName = item.disease_profile?.disease_name || item.class_name
  const confidence = (item.confidence * 100).toFixed(1)
  chatStore.setDetectionContext({
    class_id: item.class_id,
    disease_name: diseaseName,
    detection_context: `${item.class_name} (${confidence}%)`
  })
  const question = encodeURIComponent(
    `请针对检测出的【${diseaseName}】（检测置信度 ${confidence}%），结合番茄叶病害档案知识，给出具体的防治方案，包括农业防治、化学防治和推荐药剂。`
  )
  router.push({
    path: '/knowledge',
    query: { question }
  })
}

function handleReset() {
  resetResults()
  detectProgress.value = 0
}

function handleBatchAiConsult() {
  if (!batchResult.value) {
    ElMessage.warning('请先完成检测')
    return
  }
  chatStore.setDetectionContext({
    class_id: null,
    disease_name: '',
    detection_context: `本次批量检测共 ${batchRows.value.length} 张图片，成功 ${batchResult.value.success_count} 张，`
      + `失败 ${batchResult.value.failed_count} 张，检出目标 ${batchTotalCount.value} 个，`
      + `病害分布：${formatClassSummary(batchClassSummary.value)}`
  })
  router.push('/knowledge')
}

function handleDownload() {
  if (!detectionResult.value?.result_image) {
    ElMessage.warning('暂无结果可下载')
    return
  }
  const link = document.createElement('a')
  link.href = resultImageUrl.value
  link.download = `detection_result_${Date.now()}.jpg`
  link.click()
  ElMessage.success('开始下载')
}

onUnmounted(() => {
  stopProgressSimulation()
})
</script>

<style scoped>
.detect-page {
  width: 100%;
  padding: 24px;
  min-height: 100%;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 15px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.detect-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-section {
  padding: 24px;
}

.upload-area {
  position: relative;
  width: 100%;
  min-height: 280px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.upload-area:hover {
  border-color: var(--color-accent);
  box-shadow: 0 0 20px var(--color-accent-glow);
}

.upload-area.drag-over {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  transform: scale(1.02);
}

.upload-area.has-file {
  border-style: solid;
}

.upload-placeholder {
  text-align: center;
  padding: 40px 20px;
}

.upload-icon {
  color: var(--color-accent);
  margin-bottom: 16px;
}

.upload-text {
  font-size: 17px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.upload-info {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.preview-grid {
  width: 100%;
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-tertiary);
}

.preview-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: zoom-in;
}

.preview-item .remove-btn {
  top: 6px;
  right: 6px;
  width: 26px;
  height: 26px;
}

.preview-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  aspect-ratio: 1 / 1;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preview-add:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.remove-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.remove-btn:hover {
  background: var(--color-error);
  transform: scale(1.1);
}

.upload-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border-light);
}

.save-history {
  display: flex;
  align-items: center;
  gap: 10px;
}

.save-history-text {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.detect-btn {
  min-width: 140px;
  height: 42px;
  font-size: 15px;
  font-weight: 500;
}

.result-section {
  padding: 24px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.result-image-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.result-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: var(--radius-md);
  object-fit: contain;
  cursor: zoom-in;
}

.detecting-section {
  padding: 40px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.detecting-animation {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.detecting-icon {
  color: var(--color-accent);
  animation: spin 1.5s linear infinite;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
  animation: scan 2s ease-in-out infinite;
  border-radius: 2px;
  box-shadow: 0 0 10px var(--color-accent-glow);
}

@keyframes scan {
  0%, 100% {
    top: 0;
  }
  50% {
    top: calc(100% - 4px);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.detecting-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.detecting-text {
  font-size: 14px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.detect-progress {
  width: 200px;
  margin-top: 8px;
}

.detect-progress :deep(.el-progress-bar__inner) {
  background: var(--color-accent);
}

.stats-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-card {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
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

.time-icon {
  background: rgba(61, 153, 112, 0.15);
  color: #3D9970;
}

.model-icon {
  background: rgba(0, 116, 217, 0.15);
  color: #0074D9;
}

[data-theme="dark"] .total-icon {
  background: rgba(212, 175, 55, 0.15);
  color: #D4AF37;
}

[data-theme="dark"] .time-icon {
  background: rgba(61, 153, 112, 0.1);
}

[data-theme="dark"] .model-icon {
  background: rgba(0, 116, 217, 0.1);
}

.stat-content {
  min-width: 0;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.2;
}

.model-version {
  font-size: 16px;
  font-family: var(--font-family-mono);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 4px 0 0 0;
}

.category-section,
.detections-section {
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
  gap: 6px;
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

.detection-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 4px;
}

.detection-item {
  padding: 14px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  transition: background 0.2s ease;
}

.detection-item:hover {
  background: var(--color-bg-tertiary);
}

.detection-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
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
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}

.detection-confidence-text {
  margin-left: auto;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.detection-confidence-bar {
  height: 5px;
  background: var(--color-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.confidence-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.detection-bbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  font-family: var(--font-family-mono);
}

.disease-profile-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--color-border);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-item {
  display: flex;
  gap: 12px;
  font-size: 13px;
}

.profile-label {
  flex-shrink: 0;
  width: 72px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.profile-value {
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.profile-actions {
  margin-top: 12px;
  text-align: center;
}

.ask-btn {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  border: none;
  color: #fff;
}

.ask-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.healthy-section {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.healthy-hint {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 0;
  text-align: center;
}

.batch-section {
  padding: 20px;
}

.batch-table {
  width: 100%;
}

.batch-thumb {
  width: 56px;
  height: 42px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  cursor: zoom-in;
  background: var(--color-bg-tertiary);
}

.text-placeholder {
  color: var(--color-text-tertiary);
}

.batch-actions {
  grid-template-columns: repeat(2, 1fr);
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.action-btn {
  height: 44px;
  font-size: 14px;
  font-weight: 500;
}

.ai-btn {
  color: #fff;
  border: none;
}

.empty-section {
  padding: 60px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  color: var(--color-text-tertiary);
  opacity: 0.5;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
}

.empty-text {
  font-size: 14px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.dialog-preview-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.slide-up {
  animation: slideUp 0.4s ease forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .detect-container {
    grid-template-columns: 1fr;
  }

  .stat-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .detect-page {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .stat-cards {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .upload-actions {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .save-history {
    justify-content: center;
  }

  .detect-btn {
    width: 100%;
  }

  .upload-area {
    min-height: 200px;
  }

  .preview-grid {
    grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
    padding: 12px;
  }
}
</style>
