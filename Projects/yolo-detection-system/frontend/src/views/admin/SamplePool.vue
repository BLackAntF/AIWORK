<template>
  <div class="admin-sample-pool">
    <div class="page-header">
      <div>
        <h2 class="page-title">样本池审核</h2>
        <p class="page-subtitle">用户反馈样本审核与训练数据导出</p>
      </div>
      <el-button type="primary" :icon="Download" :loading="exporting" @click="handleExport">导出训练数据包</el-button>
    </div>

    <div class="filter-bar glass-card">
      <span class="filter-label">审核状态：</span>
      <el-radio-group v-model="statusFilter" @change="handleFilterChange">
        <el-radio-button value="pending">
          <el-badge :value="stats.pending" :max="99" :hidden="!stats.pending" class="btn-badge"><span>待审核</span></el-badge>
        </el-radio-button>
        <el-radio-button value="approved">
          <el-badge :value="stats.approved" :max="99" :hidden="!stats.approved" class="btn-badge"><span>已通过</span></el-badge>
        </el-radio-button>
        <el-radio-button value="rejected">
          <el-badge :value="stats.rejected" :max="99" :hidden="!stats.rejected" class="btn-badge"><span>已驳回</span></el-badge>
        </el-radio-button>
        <el-radio-button value=""><span>全部</span></el-radio-button>
      </el-radio-group>
    </div>

    <div class="glass-card table-card">
      <el-table v-loading="loading" :data="list" stripe>
        <el-table-column label="样本图" width="96">
          <template #default="{ row }">
            <el-image
              class="sample-thumb"
              fit="cover"
              lazy
              :src="imageUrl(row)"
              :preview-src-list="[imageUrl(row)]"
              preview-teleported
            >
              <template #error>
                <div class="thumb-error">加载失败</div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="110" show-overflow-tooltip />
        <el-table-column label="反馈类型" width="180">
          <template #default="{ row }">
            <el-tag :type="markMeta(row.mark_type).type" size="small">{{ markMeta(row.mark_type).label }}</el-tag>
            <div v-if="row.corrected_class" class="corrected-text">→ 纠正为 {{ row.corrected_class }}</div>
          </template>
        </el-table-column>
        <el-table-column label="预测结果" width="150">
          <template #default="{ row }">
            <div class="pred-class">{{ row.predicted_class || '—' }}</div>
            <div class="conf-text">{{ confText(row.predicted_confidence) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.note || '—' }}</template>
        </el-table-column>
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="96" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMeta(row.status).type" size="small">{{ statusMeta(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170">
          <template #default="{ row }">
            <template v-if="row.status === SAMPLE_STATUS.PENDING">
              <el-button type="success" link @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link @click="openRejectDialog(row)">驳回</el-button>
            </template>
            <span v-else class="review-note" :title="row.review_note || ''">{{ row.review_note || '—' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="PAGE_SIZES"
          layout="total, sizes, prev, pager, next"
          background
          @size-change="handleSizeChange"
          @current-change="fetchList"
        />
      </div>
    </div>

    <el-dialog v-model="rejectVisible" title="驳回样本" width="440px">
      <el-input
        v-model="rejectNote"
        type="textarea"
        :rows="3"
        maxlength="200"
        show-word-limit
        placeholder="请填写驳回原因（将通知提交者）"
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="primary" :loading="reviewing" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { getSamplePoolList, reviewSample, exportSamplePool } from '@/api/admin'
import { getFullUrl, formatTime, formatPercent } from '@/utils/format'

const SAMPLE_STATUS = { PENDING: 'pending', APPROVED: 'approved', REJECTED: 'rejected' }
const MARK_TYPES = {
  correct: { label: '检出正确', type: 'success' },
  misclassified: { label: '类别错误', type: 'warning' },
  missed: { label: '漏检', type: 'danger' },
  uncertain: { label: '待定', type: 'info' }
}
const REVIEW_STATUS = {
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' }
}
const FALLBACK_META = { label: '未知', type: 'info' }
const PAGE_SIZES = [10, 20, 50]
const ZIP_PREFIX = 'sample_pool'

const list = ref([])
const total = ref(0)
const stats = ref({ pending: 0, approved: 0, rejected: 0 })
const statusFilter = ref(SAMPLE_STATUS.PENDING)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const exporting = ref(false)
const reviewing = ref(false)
const rejectVisible = ref(false)
const rejectNote = ref('')
let rejectRow = null

function markMeta(type) {
  return MARK_TYPES[type] || FALLBACK_META
}

function statusMeta(status) {
  return REVIEW_STATUS[status] || FALLBACK_META
}

function imageUrl(row) {
  return getFullUrl(row.image_path)
}

function confText(value) {
  return value == null ? '—' : formatPercent(value, 1)
}

async function fetchList() {
  loading.value = true
  try {
    const data = await getSamplePoolList({
      status: statusFilter.value,
      page: page.value,
      page_size: pageSize.value
    })
    list.value = data.list || []
    total.value = data.total || 0
    if (data.stats) stats.value = data.stats
  } catch (e) {
    console.error('获取样本池列表失败', e)
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  page.value = 1
  fetchList()
}

function handleSizeChange() {
  page.value = 1
  fetchList()
}

function refreshAfterReview() {
  if (list.value.length === 1 && page.value > 1) page.value -= 1
  fetchList()
}

async function submitReview(row, status, note) {
  try {
    await reviewSample(row.id, status, note)
    ElMessage.success(status === SAMPLE_STATUS.APPROVED ? '已通过该样本' : '已驳回该样本')
    return true
  } catch (e) {
    console.error('审核操作失败', e)
    return false
  }
}

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('确认通过该样本并纳入训练数据集？', '审核确认', { type: 'warning' })
  } catch (e) {
    return
  }
  if (await submitReview(row, SAMPLE_STATUS.APPROVED, '')) refreshAfterReview()
}

function openRejectDialog(row) {
  rejectRow = row
  rejectNote.value = ''
  rejectVisible.value = true
}

async function confirmReject() {
  if (!rejectRow) return
  reviewing.value = true
  const ok = await submitReview(rejectRow, SAMPLE_STATUS.REJECTED, rejectNote.value.trim())
  reviewing.value = false
  if (ok) {
    rejectVisible.value = false
    refreshAfterReview()
  }
}

function saveBlob(blob) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${ZIP_PREFIX}_${Date.now()}.zip`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

async function handleExport() {
  exporting.value = true
  try {
    const res = await exportSamplePool()
    const blob = res?.data instanceof Blob ? res.data : new Blob([res?.data ?? res])
    saveBlob(blob)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(fetchList)
</script>

<style scoped>
.admin-sample-pool {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
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

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.filter-bar :deep(.el-radio-button__inner) {
  display: inline-flex;
  align-items: center;
}

.filter-bar :deep(.btn-badge) {
  margin-right: 6px;
}

.filter-bar :deep(.btn-badge .el-badge__content) {
  top: -10px;
  right: -16px;
}

.table-card {
  padding: 20px;
  border-radius: 12px;
}

.sample-thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: block;
}

.thumb-error {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--color-text-secondary);
  background: var(--color-bg-card, #f5f5f5);
}

.corrected-text {
  font-size: 12px;
  color: var(--color-accent);
  margin-top: 4px;
}

.pred-class {
  font-size: 13px;
  color: var(--color-text-primary);
}

.conf-text {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.review-note {
  display: inline-block;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .pager {
    justify-content: center;
  }
}
</style>
