<template>
  <div class="history-page">
    <div class="history-container">
      <div class="page-header glass-card">
        <div class="header-left">
          <h1 class="page-title">历史记录</h1>
          <p class="page-subtitle text-secondary">查看和管理您的检测历史</p>
        </div>
        <div class="header-actions">
          <el-button
            v-if="selectedIds.length > 0"
            type="danger"
            @click="handleBatchDelete"
          >
            <el-icon><Delete /></el-icon>
            <span>批量删除 ({{ selectedIds.length }})</span>
          </el-button>
        </div>
      </div>

      <div class="filter-bar glass-card">
        <div class="filter-row">
          <el-radio-group v-model="filterType" @change="handleSearch">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="image">图片</el-radio-button>
          </el-radio-group>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文件名..."
            clearable
            :prefix-icon="Search"
            class="search-input"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
          <el-button type="primary" class="btn-glow" @click="handleSearch">
            <el-icon><Search /></el-icon>
            <span>搜索</span>
          </el-button>
          <el-button @click="handleResetFilters">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </el-button>
          <el-button :loading="exporting" @click="handleExport">
            <el-icon><Download /></el-icon>
            <span>导出 CSV</span>
          </el-button>
        </div>
        <div class="filter-row advanced">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            class="date-range-picker"
            @change="handleSearch"
          />
          <el-select
            v-model="filterClassName"
            placeholder="检出病害"
            clearable
            filterable
            allow-create
            default-first-option
            class="filter-select"
            @change="handleSearch"
          >
            <el-option v-for="name in classOptions" :key="name" :label="name" :value="name" />
          </el-select>
          <el-select
            v-model="filterModelVersion"
            placeholder="模型版本"
            clearable
            filterable
            allow-create
            default-first-option
            class="filter-select"
            @change="handleSearch"
          >
            <el-option v-for="item in modelOptions" :key="item" :label="item" :value="item" />
          </el-select>
          <div class="confidence-filter">
            <span class="confidence-label">最低置信度</span>
            <el-input-number
              v-model="filterMinConfidence"
              :min="0"
              :max="1"
              :step="0.05"
              :precision="2"
              controls-position="right"
              class="confidence-input"
              @change="handleSearch"
            />
          </div>
        </div>
      </div>

      <div class="history-content" v-loading="loading">
        <el-table
          v-if="!isMobile"
          :data="historyList"
          class="history-table glass-card"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="缩略图" width="120">
            <template #default="{ row }">
              <div class="thumbnail-wrapper">
                <img
                  :src="getFullUrl(row.result_path || row.original_path)"
                  :alt="row.original_filename"
                  class="thumbnail"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="original_filename" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="file-name ellipsis">{{ row.original_filename }}</div>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.type === 'image' ? 'primary' : 'success'" size="small">
                {{ row.type === 'image' ? '图片' : '视频' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="检出病害" min-width="180">
            <template #default="{ row }">
              <div class="class-tags">
                <el-tag
                  v-for="name in splitClassNames(row.class_names)"
                  :key="name"
                  size="small"
                  effect="plain"
                  class="class-tag"
                >
                  {{ name }}
                </el-tag>
                <span v-if="splitClassNames(row.class_names).length === 0" class="text-placeholder">-</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="最高置信度" width="110">
            <template #default="{ row }">
              <span class="detection-count">
                {{ row.max_confidence !== null && row.max_confidence !== undefined
                  ? (row.max_confidence * 100).toFixed(1) + '%' : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="检测数量" width="120">
            <template #default="{ row }">
              <span class="detection-count">{{ row.detection_count || 0 }} 个</span>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="180">
            <template #default="{ row }">
              <span class="create-time">{{ formatDateTime(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link @click="goToDetail(row.id)">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button type="danger" link @click="handleDelete(row.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-else class="card-list">
          <div
            v-for="item in historyList"
            :key="item.id"
            class="history-card glass-card"
          >
            <div class="card-checkbox">
              <el-checkbox
                :model-value="selectedIds.includes(item.id)"
                @change="(val) => handleCardSelect(item.id, val)"
              />
            </div>
            <div class="card-thumbnail" @click="goToDetail(item.id)">
              <img
                :src="getFullUrl(item.result_path || item.original_path)"
                :alt="item.original_filename"
                class="thumbnail"
              />
              <el-tag
                :type="item.type === 'image' ? 'primary' : 'success'"
                size="small"
                class="type-tag"
              >
                {{ item.type === 'image' ? '图片' : '视频' }}
              </el-tag>
            </div>
            <div class="card-content">
              <div class="card-title ellipsis">{{ item.original_filename }}</div>
              <div class="card-meta">
                <span class="meta-item">
                  <el-icon><DataAnalysis /></el-icon>
                  {{ item.detection_count || 0 }} 个
                </span>
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>
                  {{ formatDateTime(item.created_at) }}
                </span>
              </div>
              <div class="card-actions">
                <el-button type="primary" size="small" @click="goToDetail(item.id)">
                  查看详情
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(item.id)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="historyList.length === 0 && !loading" class="empty-state">
          <el-icon :size="64"><Document /></el-icon>
          <h3>暂无历史记录</h3>
          <p class="text-secondary">您还没有进行过检测</p>
        </div>
      </div>

      <div class="pagination-wrapper glass-card" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="loadHistoryList"
          @current-change="loadHistoryList"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Delete, View, Document, DataAnalysis, Clock, Refresh, Download
} from '@element-plus/icons-vue'
import { getHistoryList, deleteHistory, batchDeleteHistory, exportHistory } from '@/api/history'
import { getFullUrl } from '@/utils/format'

const router = useRouter()

const loading = ref(false)
const exporting = ref(false)
const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterType = ref('all')
const searchKeyword = ref('')
const selectedIds = ref([])

const dateRange = ref([])
const filterClassName = ref('')
const filterModelVersion = ref('')
const filterMinConfidence = ref(0)

// 筛选下拉的候选项来自已加载记录，避免使用与实际数据不一致的静态列表
const classOptions = ref([])
const modelOptions = ref([])

const isMobile = computed(() => window.innerWidth < 768)

onMounted(() => {
  loadHistoryList()
  window.addEventListener('resize', handleResize)
})

function handleResize() {
}

function formatDateTime(time) {
  if (!time) return ''
  const date = new Date(time)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

function buildFilterParams() {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  if (filterType.value !== 'all') {
    params.type = filterType.value
  }
  if (searchKeyword.value.trim()) {
    params.keyword = searchKeyword.value.trim()
  }
  if (dateRange.value?.length === 2) {
    params.start_date = dateRange.value[0]
    params.end_date = dateRange.value[1]
  }
  if (filterClassName.value) {
    params.class_name = filterClassName.value
  }
  if (filterModelVersion.value) {
    params.model_version = filterModelVersion.value
  }
  if (filterMinConfidence.value > 0) {
    params.min_confidence = filterMinConfidence.value
  }
  return params
}

function collectFilterOptions(list) {
  const classes = new Set(classOptions.value)
  const models = new Set(modelOptions.value)
  list.forEach((row) => {
    splitClassNames(row.class_names).forEach(name => classes.add(name))
    if (row.model_version) models.add(row.model_version)
  })
  classOptions.value = [...classes].sort()
  modelOptions.value = [...models].sort()
}

function splitClassNames(value) {
  if (!value) return []
  return String(value).split(',').map(name => name.trim()).filter(Boolean)
}

function handleSearch() {
  currentPage.value = 1
  loadHistoryList()
}

function handleResetFilters() {
  filterType.value = 'all'
  searchKeyword.value = ''
  dateRange.value = []
  filterClassName.value = ''
  filterModelVersion.value = ''
  filterMinConfidence.value = 0
  handleSearch()
}

async function loadHistoryList() {
  loading.value = true
  try {
    const res = await getHistoryList(buildFilterParams())
    historyList.value = res.list || []
    total.value = res.total || 0
    collectFilterOptions(historyList.value)
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const filters = buildFilterParams()
    delete filters.page
    delete filters.page_size
    const response = await exportHistory(filters)
    const disposition = response.headers?.['content-disposition'] || ''
    const matched = disposition.match(/filename="?([^";]+)"?/)
    const filename = matched ? matched[1] : `history_${Date.now()}.csv`

    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    // 错误提示已由拦截器统一处理
  } finally {
    exporting.value = false
  }
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
}

function handleCardSelect(id, checked) {
  if (checked) {
    if (!selectedIds.value.includes(id)) {
      selectedIds.value.push(id)
    }
  } else {
    selectedIds.value = selectedIds.value.filter(sid => sid !== id)
  }
}

function goToDetail(id) {
  router.push(`/history/${id}`)
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteHistory(id)
    ElMessage.success('删除成功')
    loadHistoryList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条记录吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await batchDeleteHistory(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadHistoryList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}
</script>

<style scoped>
.history-page {
  padding: 20px;
  min-height: 100%;
}

.history-container {
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
  padding: 24px 28px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  margin: 0;
}

.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input {
  width: 280px;
  margin-left: auto;
}

.date-range-picker {
  width: 300px;
}

.filter-select {
  width: 180px;
}

.confidence-filter {
  display: flex;
  align-items: center;
  gap: 10px;
}

.confidence-label {
  font-size: 13px;
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.confidence-input {
  width: 130px;
}

.class-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.class-tag {
  border-radius: 10px;
}

.text-placeholder {
  color: var(--color-text-tertiary);
}

.history-content {
  min-height: 400px;
}

.history-table {
  overflow: hidden;
}

.thumbnail-wrapper {
  width: 80px;
  height: 60px;
  overflow: hidden;
  border-radius: var(--radius-sm);
  background: var(--color-bg-tertiary);
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-name {
  font-weight: 500;
}

.detection-count {
  color: var(--color-accent);
  font-weight: 600;
}

.create-time {
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.history-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-checkbox {
  display: flex;
  align-items: center;
}

.card-thumbnail {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
  border-radius: var(--radius-md);
  cursor: pointer;
  background: var(--color-bg-tertiary);
}

.card-thumbnail .thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.type-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item .el-icon {
  color: var(--color-accent);
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.card-actions .el-button {
  flex: 1;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--color-text-tertiary);
}

.empty-state .el-icon {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
}

@media (max-width: 768px) {
  .history-page {
    padding: 12px;
  }

  .history-container {
    gap: 12px;
  }

  .page-header {
    padding: 16px 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .filter-bar {
    padding: 12px 16px;
    gap: 12px;
  }

  .filter-row {
    gap: 10px;
  }

  .search-input {
    width: 100%;
    margin-left: 0;
  }

  .date-range-picker,
  .filter-select {
    width: 100%;
  }

  .confidence-filter {
    width: 100%;
  }

  .confidence-input {
    flex: 1;
  }

  .card-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .history-page {
    padding: 8px;
  }

  .page-header {
    padding: 12px 16px;
  }

  .page-title {
    font-size: 18px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .pagination-wrapper {
    padding: 12px;
  }
}
</style>
