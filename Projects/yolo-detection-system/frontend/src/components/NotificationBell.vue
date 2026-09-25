<template>
  <el-popover
    placement="bottom-end"
    :width="340"
    trigger="click"
    popper-class="notification-popper"
    @show="loadRecent"
  >
    <template #reference>
      <el-badge
        :value="notificationStore.unreadCount"
        :max="99"
        :hidden="notificationStore.unreadCount === 0"
        class="bell-badge"
      >
        <button class="collapse-btn bell-btn" type="button" aria-label="通知">
          <el-icon :size="20"><Bell /></el-icon>
        </button>
      </el-badge>
    </template>

    <div class="bell-panel">
      <div class="bell-panel-head">
        <span class="bell-panel-title">通知</span>
        <el-button
          link
          type="primary"
          size="small"
          :disabled="notificationStore.unreadCount === 0"
          @click="handleMarkAllRead"
        >
          全部已读
        </el-button>
      </div>

      <div v-loading="loading" class="bell-list">
        <el-empty
          v-if="!loading && recentList.length === 0"
          description="暂无通知"
          :image-size="60"
        />
        <div
          v-for="item in recentList"
          :key="item.id"
          class="bell-item"
          :class="{ 'is-unread': !item.is_read }"
          @click="handleOpen(item)"
        >
          <div class="bell-item-head">
            <span class="bell-item-title">{{ item.title }}</span>
            <span v-if="!item.is_read" class="bell-dot" />
          </div>
          <p class="bell-item-content">{{ item.content }}</p>
          <span class="bell-item-time">{{ formatTime(item.created_at) }}</span>
        </div>
      </div>

      <div class="bell-panel-foot">
        <el-button link type="primary" size="small" @click="goToNotifications">
          查看全部通知
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'
import { getNotifications } from '@/api/notifications'
import { useNotificationStore } from '@/store/modules/notification'
import { formatTime } from '@/utils/format'

const RECENT_SIZE = 5

const router = useRouter()
const notificationStore = useNotificationStore()
const recentList = ref([])
const loading = ref(false)

async function loadRecent() {
  loading.value = true
  try {
    const res = await getNotifications({ page: 1, page_size: RECENT_SIZE })
    recentList.value = res?.list || []
    notificationStore.unreadCount = res?.unread_count || 0
  } catch (e) {
    recentList.value = []
  } finally {
    loading.value = false
  }
}

async function handleMarkAllRead() {
  try {
    await notificationStore.markAllRead()
    recentList.value = recentList.value.map((item) => ({ ...item, is_read: true }))
    ElMessage.success('已全部标记为已读')
  } catch (e) {
    // 拦截器已提示错误
  }
}

async function handleOpen(item) {
  if (!item.is_read) {
    try {
      await notificationStore.markRead(item.id)
      item.is_read = true
    } catch (e) {
      // 标记失败不阻断跳转
    }
  }
  if (item.related_type === 'detection' && item.related_id) {
    router.push(`/history/${item.related_id}`)
  } else if (item.related_type === 'knowledge' && item.related_id) {
    router.push(`/knowledge-list/${item.related_id}`)
  } else {
    goToNotifications()
  }
}

function goToNotifications() {
  router.push('/notifications')
}
</script>

<style scoped>
.bell-badge {
  display: flex;
  align-items: center;
}

.bell-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-primary);
  transition: all 0.3s ease;
}

.bell-btn:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-accent);
}

.bell-panel-head,
.bell-panel-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bell-panel-head {
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.bell-panel-foot {
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
  justify-content: center;
}

.bell-panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.bell-list {
  max-height: 320px;
  overflow-y: auto;
}

.bell-item {
  padding: 10px 4px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background 0.2s ease;
}

.bell-item:hover {
  background: var(--color-bg-tertiary);
}

.bell-item-head {
  display: flex;
  align-items: center;
  gap: 6px;
}

.bell-item-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.bell-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
}

.bell-item-content {
  margin: 4px 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bell-item-time {
  font-size: 11px;
  color: var(--color-text-disabled);
}
</style>