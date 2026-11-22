<template>
  <div class="samples-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">我的样本</h1>
        <p class="page-subtitle">查看检测反馈、类别纠正与管理员审核结果</p>
      </div>
      <el-button type="primary" @click="router.push('/history')">前往检测历史</el-button>
    </div>

    <div class="glass-card table-card">
      <el-table v-loading="loading" :data="list" empty-text="暂无样本反馈，可在检测详情中提交">
        <el-table-column label="样本图" width="100">
          <template #default="{ row }">
            <el-image
              class="sample-thumb"
              fit="cover"
              lazy
              :src="getFullUrl(row.image_path)"
              :preview-src-list="[getFullUrl(row.image_path)]"
              preview-teleported
            >
              <template #error><div class="thumb-error">加载失败</div></template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column label="反馈类型" width="150">
          <template #default="{ row }">
            <el-tag :type="markMeta(row.mark_type).type" size="small">{{ markMeta(row.mark_type).label }}</el-tag>
            <el-tag v-if="row.auto_created" type="info" size="small" class="auto-tag">自动收录</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预测结果" min-width="140">
          <template #default="{ row }">
            <div>{{ row.predicted_class || '—' }}</div>
            <div class="secondary-text">{{ confidenceText(row.predicted_confidence) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="纠正类别" min-width="130">
          <template #default="{ row }">{{ row.corrected_class || '—' }}</template>
        </el-table-column>
        <el-table-column label="备注" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.note || '—' }}</template>
        </el-table-column>
        <el-table-column label="审核状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusMeta(row.status).type" size="small">{{ statusMeta(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_note" label="审核说明" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.review_note || '—' }}</template>
        </el-table-column>
        <el-table-column label="提交时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/history/${row.history_id}`)">查看检测</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          @size-change="handleSizeChange"
          @current-change="fetchList"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getMySamples } from '@/api/history'
import { formatPercent, formatTime, getFullUrl } from '@/utils/format'

const router = useRouter()
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)

const MARK_TYPES = {
  correct: { label: '标注正确', type: 'success' },
  misclassified: { label: '识别错误', type: 'warning' },
  missed: { label: '漏检', type: 'danger' },
  uncertain: { label: '不确定', type: 'info' }
}
const REVIEW_STATUS = {
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' }
}
const FALLBACK = { label: '未知', type: 'info' }

function markMeta(type) {
  return MARK_TYPES[type] || FALLBACK
}

function statusMeta(status) {
  return REVIEW_STATUS[status] || FALLBACK
}

function confidenceText(value) {
  return value == null ? '无置信度' : `置信度 ${formatPercent(value, 1)}`
}

async function fetchList() {
  loading.value = true
  try {
    const data = await getMySamples({ page: page.value, page_size: pageSize.value })
    list.value = data.list || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSizeChange() {
  page.value = 1
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.samples-page {
  max-width: 1500px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.page-title {
  margin: 0 0 6px;
  font-size: 24px;
}

.page-subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.table-card {
  padding: 20px;
  overflow: hidden;
}

.sample-thumb {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  background: var(--color-bg-tertiary);
}

.thumb-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.auto-tag {
  margin-left: 6px;
}

.secondary-text {
  margin-top: 4px;
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .table-card {
    padding: 12px;
  }
}
</style>
