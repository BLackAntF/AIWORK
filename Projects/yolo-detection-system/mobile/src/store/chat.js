/**
 * AI 问答状态管理
 * 管理会话列表、当前会话、消息记录
 */
import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    currentSessionId: null,
    messages: [],
    sessions: []
  }),

  actions: {
    /** 切换会话 */
    setSession(sessionId) {
      this.currentSessionId = sessionId
      this.messages = []
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
