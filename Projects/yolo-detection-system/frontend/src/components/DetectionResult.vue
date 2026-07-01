<template>
  <div class="detection-result">
    <div class="result-section glass-card">
      <h3 class="section-title">检测结果</h3>
      <div v-if="imageUrl" class="result-image-wrapper">
        <img :src="imageUrl" alt="检测结果" class="result-image" />
      </div>
      <div v-else class="no-image-placeholder">
        <el-icon :size="48"><Picture /></el-icon>
        <p>暂无检测图片</p>
      </div>
    </div>

    <div class="stats-section">
      <div class="stat-card glass-card">
        <div class="stat-icon total-icon">
          <el-icon :size="28"><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ totalCount }}</p>
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
          <p class="stat-value">{{ formatTime(result?.inference_time) }}</p>
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

    <div v-if="result?.detections?.length > 0" class="detections-section glass-card">
      <h3 class="section-title">检测明细</h3>
      <div class="detection-list">
        <div
          v-for="(item, index) in result.detections"
          :key="index"
          class="detection-item"
        >
          <span class="detection-index">{{ index + 1 }}</span>
          <span class="detection-tag" :style="{ backgroundColor: getCategoryColor(item.class_name) + '20', color: getCategoryColor(item.class_name) }">
            {{ item.class_name }}
          </span>
          <span class="detection-confidence">置信度: {{ (item.confidence * 100).toFixed(1) }}%</span>
          <span v-if="item.bbox" class="detection-bbox">
            [{{ item.bbox.join(', ') }}]
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Picture, DataAnalysis, CollectionTag, Timer } from '@element-plus/icons-vue'

const props = defineProps({
  result: {
    type: Object,
    default: () => ({})
  },
  imageUrl: {
    type: String,
    default: ''
  }
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
  if (props.result?.total_count !== undefined) {
    return props.result.total_count
  }
  return props.result?.detections?.length || 0
})

const categoryDistribution = computed(() => {
  if (props.result?.category_distribution) {
    return Object.entries(props.result.category_distribution).map(([name, count]) => ({
      name,
      count
    })).sort((a, b) => b.count - a.count)
  }
  if (props.result?.detections) {
    const distribution = {}
    props.result.detections.forEach(item => {
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

function formatTime(time) {
  if (!time) return '0ms'
  if (time < 1000) {
    return time.toFixed(0) + 'ms'
  }
  return (time / 1000).toFixed(2) + 's'
}
</script>

<style scoped>
.detection-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 16px;
}

.result-section {
  padding: 20px;
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
}

.no-image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-tertiary);
}

.no-image-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
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
  color: var(--color-text-primary);
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

.detections-section {
  padding: 20px;
}

.detection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  transition: background 0.2s ease;
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

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .detection-bbox {
    display: none;
  }
}
</style>
