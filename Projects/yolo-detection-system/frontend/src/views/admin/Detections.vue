<template>
  <div class="admin-detections">
    <div class="page-header">
      <h2 class="page-title">检测记录</h2>
      <p class="page-subtitle">查看和管理所有用户的检测记录</p>
    </div>

    <div class="stats-row">
      <div class="mini-stat glass-card">
        <div class="mini-stat-label">总检测数</div>
        <div class="mini-stat-value">{{ stats.total_count || 0 }}</div>
      </div>
      <div class="mini-stat glass-card">
        <div class="mini-stat-label">今日检测</div>
        <div class="mini-stat-value">{{ stats.today_count || 0 }}</div>
      </div>
      <div class="mini-stat glass-card">
        <div class="mini-stat-label">平均耗时</div>
        <div class="mini-stat-value">{{ stats.avg_processing_time || 0 }}s</div>
      </div>
    </div>

    <div class="filter-bar glass-card">
      <div class="filter-left">
        <el-input
          v-model="filters.user_id"
          placeholder="用户ID筛选"
          clearable
          @keyup.enter="fetchList"
          style="width: 140px"
        />
        <el-select v-model="filters.type" placeholder="类型筛选" clearable @change="fetchList" style="width: 120px">
          <el-option label="全部类型" value="" />
          <el-option label="图片" value="image" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="handleDateChange"
          style="width: 260px"
        />
      </div>
      <div class="filter-right">
        <el-button type="primary" :icon="Refresh" @click="fetchList">刷新</el-button>
      </div>
    </div>

    <div class="table-card glass-card">
      <div class="table-header">
        <h3 class="table-title">检测记录列表</h3>
        <div class="table-actions">
          <span class="total-text">共 {{ total }} 条</span>
          <el-button
            type="danger"
            :icon="Delete"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            批量删除
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="detectionList"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="type" label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'image' ? 'success' : 'primary'" effect="light" size="small">
              {{ row.type === 'image' ? '图片' : '视频' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="original_filename" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="detection_count" label="检测数" width="90" align="center">
          <template #default="{ row }">
            <span class="count-number">{{ row.detection_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="processing_time" label="处理耗时" width="100" align="center">
          <template #default="{ row }">
            <span class="time-number">{{ row.processing_time?.toFixed(3) }}s</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="170" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleViewDetail(row)">详情</el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchList"
          @current-change="fetchList"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="检测详情"
      width="700px"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border size="default">
          <el-descriptions-item label="记录ID">{{ currentDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ currentDetail.username }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ currentDetail.type === 'image' ? '图片' : '视频' }}
          </el-descriptions-item>
          <el-descriptions-item label="文件名">{{ currentDetail.original_filename }}</el-descriptions-item>
          <el-descriptions-item label="检测数量">{{ currentDetail.detection_count }}</el-descriptions-item>
          <el-descriptions-item label="处理耗时">{{ currentDetail.processing_time?.toFixed(3) }}s</el-descriptions-item>
          <el-descriptions-item label="模型版本">{{ currentDetail.model_version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="检测时间">{{ formatTime(currentDetail.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentDetail.result_image" class="detail-image">
          <h4>检测结果图</h4>
          <el-image
            :src="getFullUrl(currentDetail.result_image)"
            :preview-src-list="[getFullUrl(currentDetail.result_image)]"
            fit="contain"
            style="width: 100%; max-height: 300px; border-radius: 8px;"
          />
        </div>

        <div v-if="currentDetail.detections?.length" class="detail-detections">
          <h4>检测目标列表</h4>
          <div class="detection-tags">
            <el-tag
              v-for="(det, idx) in currentDetail.detections.slice(0, 10)"
              :key="idx"
              type="info"
              effect="light"
              style="margin: 4px;"
            >
              {{ det.class_name }} ({{ (det.confidence * 100).toFixed(1) }}%)
            </el-tag>
          </div>
          <div v-if="currentDetail.detections.length > 10" class="more-text">
            共 {{ currentDetail.detections.length }} 个目标
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete } from '@element-plus/icons-vue'
import {
  getDetectionList, getDetectionDetail, deleteDetection,
  batchDeleteDetection, getDetectionStats
} from '@/api/admin'
import { formatTime, getFullUrl } from '@/utils/format'

const loading = ref(false)
const detectionList = ref([])
const total = ref(0)
const selectedIds = ref([])
const stats = ref({})
const dateRange = ref([])

const filters = reactive({
  page: 1,
  page_size: 20,
  user_id: '',
  type: '',
  start_date: '',
  end_date: ''
})

// 详情
const detailDialogVisible = ref(false)
const currentDetail = ref(null)

function handleDateChange(val) {
  if (val && val.length === 2) {
    filters.start_date = val[0]
    filters.end_date = val[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  fetchList()
}

async function fetchStats() {
  try {
    stats.value = await getDetectionStats()
  } catch (e) {
    stats.value = {
      total_count: 0,
      today_count: 0,
      avg_processing_time: 0
    }
  }
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: filters.page,
      page_size: filters.page_size
    }
    if (filters.user_id) params.user_id = filters.user_id
    if (filters.type) params.type = filters.type
    if (filters.start_date) params.start_date = filters.start_date
    if (filters.end_date) params.end_date = filters.end_date

    const res = await getDetectionList(params)
    detectionList.value = res.list || []
    total.value = res.total || 0
  } catch (e) {
    detectionList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
}

async function handleViewDetail(row) {
  try {
    currentDetail.value = await getDetectionDetail(row.id)
    detailDialogVisible.value = true
  } catch (e) {
    currentDetail.value = row
    detailDialogVisible.value = true
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条检测记录吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteDetection(row.id)
    ElMessage.success('删除成功')
    fetchList()
    fetchStats()
  } catch (e) {}
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条记录吗？`,
      '确认批量删除',
      { type: 'warning' }
    )
    await batchDeleteDetection(selectedIds.value)
    ElMessage.success('批量删除成功')
    fetchList()
    fetchStats()
  } catch (e) {}
}

onMounted(() => {
  fetchStats()
  fetchList()
})
</script>

<style scoped>
.admin-detections {
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.mini-stat {
  padding: 16px 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.mini-stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-mono);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-left,
.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-card {
  border-radius: 12px;
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-text {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.count-number,
.time-number {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--color-text-primary);
}

.time-text {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-image h4,
.detail-detections h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.detail-image {
  background: var(--color-bg-tertiary);
  padding: 16px;
  border-radius: 8px;
}

.detail-detections {
  background: var(--color-bg-tertiary);
  padding: 16px;
  border-radius: 8px;
}

.detection-tags {
  display: flex;
  flex-wrap: wrap;
}

.more-text {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--color-bg-tertiary);
  --el-table-border-color: var(--color-border);
  --el-table-text-color: var(--color-text-primary);
  --el-table-header-text-color: var(--color-text-secondary);
}

:deep(.el-table th.el-table__cell) {
  background-color: var(--color-bg-tertiary) !important;
  font-weight: 600;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
}

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left,
  .filter-right {
    width: 100%;
  }
}
</style>
