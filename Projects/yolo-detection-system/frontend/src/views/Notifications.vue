<template>
  <div class="notifications-page">
    <div class="notifications-container">
      <div class="page-header glass-card">
        <div class="header-left">
          <h1 class="page-title">通知中心</h1>
          <p class="page-subtitle text-secondary">
            共 {{ total }} 条通知，其中 {{ notificationStore.unreadCount }} 条未读
          </p>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            class="btn-glow"
            :disabled="notificationStore.unreadCount === 0"
            @click="handleMarkAllRead"
          >
            <el-icon><Select /></el-icon>
            <span>全部已读</span>
          </el-button>
        </div>
      </div>

      <div class="filter-bar glass-card">
        <el-radio-group v-model="filterRead" @change="handleFilterChange">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="unread">未读</el-radio-button>
          <el-radio-button value="read">已读</el-radio-button>
        </el-radio-group>
      </div>

      <div class="notifications-content" v-loading="loading">
        <el-empty
          v-if="!loading && list.length === 0"
          description="暂无通知"
        />
        <div
          v-for="item in list"
          :key="item.id"
          class="notification-item glass-card"
          :class="{ 'is-unread': !item.is_read }"
        >
          <div class="item-main" @click="handleOpen(item)">
            <div class="item-head">
              <el-tag :type="tagType(item.type)" size="small" effect="plain">
                {{ typeLabel(item.type) }}
              </el-tag>
              <span class="item-title">{{ item.title }}</span>
              <span v-if="!item.is_read" class="unread-dot"></span>
            </div>
            <p class="item-content">{{ item.content }}</p>
            <span class="item-time">{{ formatTime(item.created_at) }}</span>
          </div>
          <div class="item-actions">
            <el-button
              v-if="!item.is_read"
              type="primary"
              link
              @click="handleRead(item)"
            >
              标记已读
            </el-button>
            <el-button type="danger" link @click="handleDelete(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <div class="pagination-wrapper glass-card" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Select, Delete } from '@element-plus/icons-vue'
import { getNotifications, deleteNotification } from '@/api/notifications'
import { useNotificationStore } from '@/store/modules/notification'
import { formatTime } from '@/utils/format'

const TYPE_LABELS = {
  detection_completed: '检测完成',
  knowledge_approved: '审核通过',
  knowledge_rejected: '审核未通过',
  system: '系统通知'
}

const TYPE_TAGS = {
  detection_completed: 'primary',
  knowledge_approved: 'success',
  knowledge_rejected: 'danger',
  system: 'info'
}

const router = useRouter()
const notificationStore = useNotificationStore()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterRead = ref('all')

onMounted(() => {
  loadList()
})

function typeLabel(type) {
  return TYPE_LABELS[type] || '通知'
}

function tagType(type) {
  return TYPE_TAGS[type] || 'info'
}

async function loadList() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterRead.value === 'unread') {
      params.is_read = 'false'
    } else if (filterRead.value === 'read') {
      params.is_read = 'true'
    }
    const res = await getNotifications(params)
    list.value = res?.list || []
    total.value = res?.total || 0
    notificationStore.unreadCount = res?.unread_count || 0
  } catch (error) {
    ElMessage.error('加载通知失败')
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  currentPage.value = 1
  loadList()
}

async function handleOpen(item) {
  if (!item.is_read) {
    await handleRead(item)
  }
  if (item.related_type === 'detection' && item.related_id) {
    router.push(`/history/${item.related_id}`)
  } else if (item.related_type === 'knowledge' && item.related_id) {
    router.push(`/knowledge-list/${item.related_id}`)
  }
}

async function handleRead(item) {
  if (item.is_read) return
  try {
    await notificationStore.markRead(item.id)
    item.is_read = true
    if (filterRead.value === 'unread') {
      loadList()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleMarkAllRead() {
  try {
    const updated = await notificationStore.markAllRead()
    ElMessage.success(updated > 0 ? `已标记 ${updated} 条为已读` : '没有未读通知')
    loadList()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(item) {
  try {
    await ElMessageBox.confirm('确定要删除这条通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteNotification(item.id)
    ElMessage.success('删除成功')
    if (!item.is_read) {
      notificationStore.unreadCount = Math.max(0, notificationStore.unreadCount - 1)
    }
    loadList()
  } catch (error) {
    // 用户取消或请求失败，均不额外处理
  }
}
</script>

<style scoped>
.notifications-page {
  min-height: 100%;
}

.notifications-container {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
}

.page-title {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
}

.notifications-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 24px;
  transition: transform 0.2s ease;
}

.notification-item.is-unread {
  border-left: 3px solid var(--color-accent);
}

.item-main {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.item-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent-glow);
}

.item-content {
  margin: 8px 0 6px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.item-time {
  font-size: 12px;
  color: var(--color-text-disabled);
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .notification-item {
    flex-direction: column;
    padding: 16px;
  }

  .item-actions {
    align-self: flex-end;
  }
}
</style>