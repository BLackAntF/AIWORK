/**
 * AI 问答状态管理
 * 管理会话列表、当前会话、消息记录
 */
import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    currentSessionId: null,
    messages: [],
    sessions: [],
    pendingDetection: null
  }),

  actions: {
    /** 切换会话 */
    setSession(sessionId) {
      this.currentSessionId = sessionId
      this.messages = []
    },

    /** 记录待带入问答的检测结果（跨 tabBar 页面传递） */
    setPendingDetection(payload) {
      this.pendingDetection = payload
    },

    /** 清除待带入的检测结果 */
    clearPendingDetection() {
      this.pendingDetection = null
    },

    /** 添加一条消息 */
    addMessage(msg) {
      this.messages.push(msg)
    },

    /** 重置消息列表 */
    clearMessages() {
      this.messages = []
    },

    /** 设置会话列表 */
    setSessions(list) {
      this.sessions = list
    }
  }
})
