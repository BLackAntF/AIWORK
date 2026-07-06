<template>
  <div class="admin-operation-log">
    <div class="page-header">
      <h2 class="page-title">操作日志</h2>
      <p class="page-subtitle">记录系统所有操作行为</p>
    </div>

    <div class="filter-bar glass-card">
      <div class="filter-left">
        <el-select v-model="filters.action" placeholder="操作类型" clearable @change="fetchList" style="width: 150px">
          <el-option label="全部类型" value="" />
          <el-option label="登录" value="login" />
          <el-option label="登出" value="logout" />
          <el-option label="检测" value="detect" />
          <el-option label="用户创建" value="user_create" />
          <el-option label="用户删除" value="user_delete" />
          <el-option label="用户状态变更" value="user_status" />
          <el-option label="知识添加" value="knowledge_add" />
          <el-option label="知识编辑" value="knowledge_edit" />
          <el-option label="知识删除" value="knowledge_delete" />
          <el-option label="配置更新" value="config_update" />
          <el-option label="模型上传" value="model_upload" />
        </el-select>
        <el-select v-model="filters.level" placeholder="日志级别" clearable @change="fetchList" style="width: 120px">
          <el-option label="全部级别" value="" />
          <el-option label="INFO" value="info" />
          <el-option label="WARN" value="warn" />
          <el-option label="ERROR" value="error" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="fetchList"
          style="width: 300px"
        />
      </div>
      <div class="filter-right">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索用户名/操作描述"
          clearable
          @keyup.enter="fetchList"
          style="width: 240px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" :icon="Refresh" @click="fetchList">刷新</el-button>
      </div>
    </div>

    <div class="table-card glass-card">
      <div class="table-header">
        <h3 class="table-title">日志列表</h3>
        <div class="table-actions">
          <span class="total-text">共 {{ total }} 条</span>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="logList"
        stripe
        style="width: 100%"
        :row-class-name="tableRowClassName"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="username" label="操作用户" width="120" align="center">
          <template #default="{ row }">
            <el-avatar :size="28" class="cell-avatar">
              {{ row.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="cell-username">{{ row.username || '系统' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)" effect="light" size="small">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="操作描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="150" align="center">
          <template #default="{ row }">
            <span class="ip-text">{{ row.ip_address || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)" effect="dark" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getOperationLogList } from '@/api/admin'
import { formatTime } from '@/utils/format'

const loading = ref(false)
const logList = ref([])
const total = ref(0)

const filters = reactive({
  page: 1,
  page_size: 20,
  action: '',
  level: '',
  keyword: '',
  dateRange: null
})

function tableRowClassName() {
  return 'table-row-custom'
}

function getActionLabel(action) {
  const actionMap = {
    login: '登录',
    logout: '登出',
    detect: '检测',
    user_create: '用户创建',
    user_delete: '用户删除',
    user_status: '用户状态变更',
    knowledge_add: '知识添加',
    knowledge_edit: '知识编辑',
    knowledge_delete: '知识删除',
    config_update: '配置更新',
    model_upload: '模型上传',
    knowledge_import: '知识导入',
    sync_vector: '向量同步'
  }
  return actionMap[action] || action
}

function getActionTagType(action) {
  const typeMap = {
    login: 'success',
    logout: 'info',
    detect: 'primary',
    user_create: 'success',
    user_delete: 'danger',
    user_status: 'warning',
    knowledge_add: 'success',
    knowledge_edit: 'primary',
    knowledge_delete: 'danger',
    config_update: 'warning',
    model_upload: 'success',
    knowledge_import: 'success',
    sync_vector: 'primary'
  }
  return typeMap[action] || 'info'
}

function getLevelTagType(level) {
  const typeMap = {
    info: 'primary',
    warn: 'warning',
    error: 'danger'
  }
  return typeMap[level] || 'info'
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: filters.page,
      page_size: filters.page_size
    }
    if (filters.action) params.action = filters.action
    if (filters.level) params.level = filters.level
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0].toISOString().split('T')[0]
      params.end_date = filters.dateRange[1].toISOString().split('T')[0]
    }

    const res = await getOperationLogList(params)
    logList.value = res.list || []
    total.value = res.total || 0
  } catch (e) {
    logList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.admin-operation-log {
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
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.total-text {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.cell-avatar {
  background: var(--color-accent);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  margin-right: 8px;
}

.cell-username {
  color: var(--color-text-primary);
  font-weight: 500;
}

.ip-text {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--color-text-secondary);
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

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--color-bg-tertiary);
  --el-table-border-color: var(--color-border);
  --el-table-text-color: var(--color-text-primary);
  --el-table-header-text-color: var(--color-text-secondary);
}

:deep(.el-table .el-table__row:hover > td) {
  background-color: var(--color-bg-tertiary) !important;
}

:deep(.el-table th.el-table__cell) {
  background-color: var(--color-bg-tertiary) !important;
  font-weight: 600;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--color-text-secondary);
  --el-pagination-hover-color: var(--color-accent);
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left,
  .filter-right {
    width: 100%;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>