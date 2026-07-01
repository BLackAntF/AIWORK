<template>
  <div class="admin-users">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <p class="page-subtitle">管理系统用户账户与权限</p>
    </div>

    <div class="filter-bar glass-card">
      <div class="filter-left">
        <el-select v-model="filters.role" placeholder="角色筛选" clearable @change="fetchList" style="width: 120px">
          <el-option label="全部角色" value="" />
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="fetchList" style="width: 120px">
          <el-option label="全部状态" value="" />
          <el-option label="已启用" value="active" />
          <el-option label="已禁用" value="inactive" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索用户名/邮箱"
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
        <h3 class="table-title">用户列表</h3>
        <div class="table-actions">
          <span class="total-text">共 {{ total }} 条</span>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        style="width: 100%"
        :row-class-name="tableRowClassName"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="username" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="32" class="cell-avatar">
                {{ row.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="cell-username">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" effect="light" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" size="small">
              {{ row.is_active ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detection_count" label="检测数" width="100" align="center">
          <template #default="{ row }">
            <span class="count-number">{{ row.detection_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.role === 'user'"
              type="warning"
              size="small"
              link
              @click="handleUpdateRole(row)"
            >
              设为管理员
            </el-button>
            <el-button
              v-else
              type="info"
              size="small"
              link
              @click="handleUpdateRole(row)"
            >
              取消管理员
            </el-button>
            <el-button
              :type="row.is_active ? 'info' : 'success'"
              size="small"
              link
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getUserList, updateUserStatus, updateUserRole, deleteUser } from '@/api/admin'
import { formatTime } from '@/utils/format'

const loading = ref(false)
const userList = ref([])
const total = ref(0)

const filters = reactive({
  page: 1,
  page_size: 20,
  role: '',
  status: '',
  keyword: ''
})

function tableRowClassName() {
  return 'table-row-custom'
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: filters.page,
      page_size: filters.page_size
    }
    if (filters.role) params.role = filters.role
    if (filters.status) params.status = filters.status
    if (filters.keyword) params.keyword = filters.keyword

    const res = await getUserList(params)
    userList.value = res.list || []
    total.value = res.total || 0
  } catch (e) {
    userList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function handleToggleStatus(row) {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      '确认操作',
      { type: 'warning' }
    )
    await updateUserStatus(row.id, !row.is_active)
    ElMessage.success(`${action}成功`)
    fetchList()
  } catch (e) {}
}

async function handleUpdateRole(row) {
  const newRole = row.role === 'admin' ? 'user' : 'admin'
  const action = newRole === 'admin' ? '设为管理员' : '取消管理员'
  try {
    await ElMessageBox.confirm(
      `确定要将用户 "${row.username}" ${action} 吗？`,
      '确认操作',
      { type: 'warning' }
    )
    await updateUserRole(row.id, newRole)
    ElMessage.success('角色更新成功')
    fetchList()
  } catch (e) {}
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？此操作将同时删除该用户的所有检测记录和对话历史，且不可恢复。`,
      '确认删除',
      { type: 'error', confirmButtonText: '确认删除' }
    )
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {}
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.admin-users {
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cell-avatar {
  background: var(--color-accent);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.cell-username {
  color: var(--color-text-primary);
  font-weight: 500;
}

.count-number {
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

  .filter-right :deep(.el-input) {
    flex: 1;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
