import { defineStore } from 'pinia'
import {
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead
} from '@/api/notifications'

const POLL_INTERVAL = 60000

let pollTimer = null

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    unreadCount: 0
  }),

  actions: {
    async fetchUnreadCount() {
      try {
        const res = await getUnreadCount()
        this.unreadCount = res?.unread_count || 0
      } catch (e) {
        // 轮询失败静默处理，避免打断用户操作
      }
      return this.unreadCount
    },

    async markRead(id) {
      await markNotificationRead(id)
      if (this.unreadCount > 0) {
        this.unreadCount -= 1
      }
    },

    async markAllRead() {
      const res = await markAllNotificationsRead()
      this.unreadCount = 0
      return res?.updated_count || 0
    },

    startPolling() {
      if (pollTimer) return
      this.fetchUnreadCount()
      pollTimer = setInterval(() => this.fetchUnreadCount(), POLL_INTERVAL)
    },

    stopPolling() {
      if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
      }
      this.unreadCount = 0
    }
  }
})