<template>
  <div class="share-page">
    <div class="share-container">
      <header class="share-header glass-card">
        <p class="header-eyebrow">TOMATO LEAF DIAGNOSIS</p>
        <h1 class="header-title">番茄病害检测报告 · 分享</h1>
        <div class="header-meta">
          <el-tag size="small" type="info" effect="plain">只读分享</el-tag>
          <span class="header-note">本页面为只读分享</span>
        </div>
      </header>

      <div v-if="loading" class="share-state glass-card">
        <el-icon :size="36" class="state-icon spin-icon"><Loading /></el-icon>
        <p class="state-text">正在加载分享内容...</p>
      </div>

      <div v-else-if="errorMessage" class="share-state glass-card">
        <el-icon :size="44" class="state-icon state-error"><Warning /></el-icon>
        <p class="state-title">{{ errorMessage }}</p>
        <p class="state-text">请向分享者确认链接是否有效</p>
      </div>

      <div v-else class="share-body">
        <section class="summary-card glass-card">
          <div v-if="resultImageUrl" class="image-wrapper">
            <img :src="resultImageUrl" alt="检测结果" class="result-image" />
          </div>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">文件名</span>
              <span class="info-value ellipsis">{{ info.original_filename || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">检测时间</span>
              <span class="info-value">{{ formatTime(info.created_at) || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">模型版本</span>
              <span class="info-value">{{ info.model_version || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">检测数量</span>
              <span class="info-value">{{ info.detection_count ?? detections.length }}</span>
            </div>
          </div>
        </section>

        <section class="detections-card glass-card">
          <h2 class="section-title">
            检测明细
            <span class="section-count">共 {{ detections.length }} 条</span>
          </h2>
          <div v-if="detections.length" class="detection-list">
            <div v-for="(item, index) in detections" :key="index" class="detection-item">
              <span class="detection-index">{{ index + 1 }}</span>
              <span class="detection-tag">{{ item.class_name || item.category || '未知类别' }}</span>
              <span class="detection-confidence">{{ ((item.confidence || 0) * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <div v-else class="empty-detections">
            <el-icon :size="32"><Warning /></el-icon>
            <p>未检测到目标</p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading, Warning } from '@element-plus/icons-vue'
import { getSharedResult } from '@/api/history'
import { getFullUrl, formatTime } from '@/utils/format'

const route = useRoute()

const loading = ref(true)
const errorMessage = ref('')
const shared = ref(null)

const info = computed(() => shared.value?.history || shared.value || {})
const detections = computed(() => {
  const data = shared.value
  if (!data) return []
  if (Array.isArray(data.detections)) return data.detections
  return data.detection_result?.detections || []
})
const resultImageUrl = computed(() => {
  const path = info.value.result_image || info.value.result_path
  return path ? getFullUrl(path) : ''
})

async function loadShare() {
  const token = route.params.token
  if (!token) {
    loading.value = false
    errorMessage.value = '分享链接不存在或已被删除'
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    shared.value = await getSharedResult(token)
  } catch (error) {
    const status = error?.response?.status
    const responseMessage = error?.response?.data?.message
    if (status === 404) {
      errorMessage.value = '分享链接不存在或已被删除'
    } else if (status === 410) {
      errorMessage.value = '分享链接已过期'
    } else {
      errorMessage.value = responseMessage || '分享内容加载失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadShare)
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  padding: 32px 20px 56px;
}

.share-container {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.share-header {
  padding: 28px 32px;
}

.header-eyebrow {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--color-accent);
}

.header-title {
  margin: 0 0 10px;
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-note {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.share-state {
  padding: 64px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.state-icon {
  color: var(--color-accent);
}

.state-error {
  color: var(--color-warning);
}

.spin-icon {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.state-title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.state-text {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.share-body {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 20px;
  align-items: start;
}

.summary-card,
.detections-card {
  padding: 22px;
}

.image-wrapper {
  width: 100%;
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
  display: flex;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 18px;
}

.result-image {
  max-width: 100%;
  max-height: 460px;
  object-fit: contain;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border-light);
}

.info-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.info-label {
  flex-shrink: 0;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  min-width: 0;
  text-align: right;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 16px;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-count {
  font-size: 12px;
  font-weight: 400;
  color: var(--color-text-tertiary);
}

.detection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 460px;
  overflow-y: auto;
  padding-right: 4px;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: var(--color-bg-secondary);
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
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.detection-confidence {
  margin-left: auto;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.empty-detections {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 40px 20px;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.empty-detections p {
  margin: 0;
}

@media (max-width: 768px) {
  .share-page {
    padding: 20px 12px 40px;
  }

  .share-header {
    padding: 20px;
  }

  .header-title {
    font-size: 20px;
  }

  .share-body {
    grid-template-columns: 1fr;
  }

  .summary-card,
  .detections-card {
    padding: 16px;
  }
}
</style>
