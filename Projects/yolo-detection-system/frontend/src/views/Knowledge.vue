<template>
  <div class="knowledge-page">
    <div class="knowledge-container">
      <div class="sidebar glass-card" :class="{ 'sidebar-open': sidebarOpen }">
        <div class="sidebar-header">
          <el-button type="primary" class="btn-glow new-chat-btn" @click="createNewSession">
            <el-icon><Plus /></el-icon>
            <span>新建对话</span>
          </el-button>
        </div>
        <div class="session-list" v-loading="sessionsLoading">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="session-item"
            :class="{ active: currentSessionId === session.id }"
            @click="switchSession(session.id)"
          >
            <div class="session-info">
              <div class="session-title ellipsis">{{ session.title || '新对话' }}</div>
              <div class="session-time">{{ formatTime(session.updated_at) }}</div>
            </div>
            <el-button
              type="danger"
              link
              class="delete-btn"
              @click.stop="handleDeleteSession(session.id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <div v-if="sessions.length === 0 && !sessionsLoading" class="empty-sessions">
            <el-icon :size="32"><ChatDotRound /></el-icon>
            <p>暂无对话记录</p>
          </div>
        </div>
      </div>

      <div class="sidebar-mask" v-if="sidebarOpen" @click="sidebarOpen = false"></div>

      <div class="chat-main">
        <div class="chat-header glass-card">
          <el-button class="menu-btn" link @click="sidebarOpen = !sidebarOpen">
            <el-icon><Menu /></el-icon>
          </el-button>
          <div class="chat-title ellipsis">{{ currentSession?.title || 'AI 知识问答' }}</div>
          <div class="header-actions">
            <el-button type="danger" link @click="handleClearChat">
              <el-icon><Delete /></el-icon>
              <span class="hide-mobile">清空对话</span>
            </el-button>
          </div>
        </div>

        <div class="chat-messages" ref="messagesContainer" v-loading="messagesLoading">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-item"
            :class="{ 'user-message': msg.role === 'user', 'ai-message': msg.role === 'assistant' }"
          >
            <div class="message-avatar">
              <el-icon v-if="msg.role === 'user'"><User /></el-icon>
              <el-icon v-else><Cpu /></el-icon>
            </div>
            <div class="message-bubble">
              <div class="message-content" v-if="msg.role === 'user'">
                {{ msg.content }}
              </div>
              <div class="message-content" v-else>
                <div v-if="msg.displayContent">{{ msg.displayContent }}</div>
                <div v-else>{{ msg.content }}</div>
              </div>
              <div v-if="msg.role === 'assistant' && msg.sources && msg.sources.length > 0" class="message-sources">
                <div class="sources-title">引用来源：</div>
                <div class="source-list">
                  <div
                    v-for="(source, sIndex) in msg.sources"
                    :key="sIndex"
                    class="source-item"
                  >
                    <el-icon><Document /></el-icon>
                    <span class="source-title ellipsis">{{ source.title }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="isTyping" class="message-item ai-message">
            <div class="message-avatar">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="message-bubble">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area glass-card">
          <div v-if="detectionContext" class="detection-context-badge">
            <el-icon><Picture /></el-icon>
            <span>已附带检测上下文</span>
            <el-button link size="small" @click="clearDetectionContext">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <div class="input-wrapper">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="2"
              placeholder="输入您的问题，Ctrl+Enter 发送..."
              resize="none"
              @keydown="handleKeyDown"
              class="message-input"
            />
            <div class="input-actions">
              <el-button
                type="primary"
                class="btn-glow send-btn"
                :disabled="!inputMessage.trim() || isTyping"
                :loading="isTyping"
                @click="sendMessage"
              >
                <el-icon><Promotion /></el-icon>
                <span>发送</span>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Delete, ChatDotRound, Menu, User, Cpu,
  Document, Close, Promotion, Picture
} from '@element-plus/icons-vue'
import { askQuestion, getChatHistory, getSessions, deleteSession } from '@/api/knowledge'
import { formatRelativeTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()

const messagesContainer = ref(null)
const sidebarOpen = ref(false)
const sessionsLoading = ref(false)
const messagesLoading = ref(false)
const isTyping = ref(false)

const sessions = ref([])
const currentSessionId = ref(null)
const messages = ref([])
const inputMessage = ref('')
const detectionContext = ref(null)

const currentSession = computed(() => {
  return sessions.value.find(s => s.id === currentSessionId.value)
})

onMounted(() => {
  if (route.query.detection_context) {
    try {
      detectionContext.value = JSON.parse(decodeURIComponent(route.query.detection_context))
    } catch (e) {
      detectionContext.value = route.query.detection_context
    }
  }
  loadSessions()
})

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
  return date.toLocaleDateString()
}

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const res = await getSessions()
    sessions.value = res.data || res.data?.sessions || []
    if (sessions.value.length > 0 && !currentSessionId.value) {
      switchSession(sessions.value[0].id)
    }
  } catch (error) {
    ElMessage.error('加载会话列表失败')
  } finally {
    sessionsLoading.value = false
  }
}

async function switchSession(sessionId) {
  currentSessionId.value = sessionId
  sidebarOpen.value = false
  messagesLoading.value = true
  try {
    const res = await getChatHistory({ session_id: sessionId })
    messages.value = res.data?.messages || res.data || []
  } catch (error) {
    ElMessage.error('加载聊天记录失败')
  } finally {
    messagesLoading.value = false
    scrollToBottom()
  }
}

async function createNewSession() {
  currentSessionId.value = null
  messages.value = []
  inputMessage.value = ''
  sidebarOpen.value = false
}

async function handleDeleteSession(sessionId) {
  try {
    await ElMessageBox.confirm('确定要删除这个会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteSession(sessionId)
    ElMessage.success('删除成功')
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
      messages.value = []
    }
    loadSessions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleClearChat() {
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    messages.value = []
    ElMessage.success('已清空对话')
  } catch (error) {
  }
}

function handleKeyDown(e) {
  if (e.ctrlKey && e.key === 'Enter') {
    sendMessage()
  }
}

async function sendMessage() {
  const content = inputMessage.value.trim()
  if (!content || isTyping.value) return

  const userMsg = {
    role: 'user',
    content: content
  }
  messages.value.push(userMsg)
  inputMessage.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    const data = {
      question: content,
      session_id: currentSessionId.value
    }
    if (detectionContext.value) {
      data.detection_context = detectionContext.value
    }
    const res = await askQuestion(data)
    const aiMsg = {
      role: 'assistant',
      content: res.data?.answer || res.data?.content || '抱歉，我无法回答这个问题。',
      sources: res.data?.sources || []
    }
    if (res.data?.session_id && !currentSessionId.value) {
      currentSessionId.value = res.data.session_id
      loadSessions()
    }
    messages.value.push(aiMsg)
    startTypewriterEffect(aiMsg)
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

function startTypewriterEffect(msg) {
  if (!msg.content) return
  msg.displayContent = ''
  let index = 0
  const speed = 30
  const timer = setInterval(() => {
    if (index < msg.content.length) {
      msg.displayContent += msg.content[index]
      index++
      scrollToBottom()
    } else {
      clearInterval(timer)
    }
  }, speed)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function clearDetectionContext() {
  detectionContext.value = null
  router.replace({ query: {} })
}
</script>

<style scoped>
.knowledge-page {
  height: 100%;
  padding: 20px;
}

.knowledge-container {
  display: flex;
  height: calc(100vh - 140px);
  gap: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.sidebar {
  width: 25%;
  min-width: 280px;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  padding: 20px;
  z-index: 100;
}

.sidebar-header {
  margin-bottom: 16px;
}

.new-chat-btn {
  width: 100%;
  height: 44px;
  justify-content: center;
  gap: 8px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--color-bg-secondary);
}

.session-item:hover {
  background: var(--color-bg-tertiary);
}

.session-item.active {
  background: var(--color-accent-glow);
  border: 1px solid var(--color-accent);
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.session-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.delete-btn {
  flex-shrink: 0;
  padding: 4px;
}

.empty-sessions {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 12px;
}

.sidebar-mask {
  display: none;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  flex-shrink: 0;
}

.menu-btn {
  display: none;
  padding: 8px;
}

.chat-title {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.ai-message {
  align-self: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-accent);
  color: white;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #E07A5F, #F29780);
}

.ai-message .message-avatar {
  background: linear-gradient(135deg, #D4AF37, #E8C85A);
}

.message-bubble {
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  box-shadow: var(--shadow-sm);
  min-width: 60px;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  color: white;
}

.message-content {
  line-height: 1.7;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-sources {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.sources-title {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-bottom: 8px;
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
}

.source-item .el-icon {
  color: var(--color-accent);
  flex-shrink: 0;
}

.source-title {
  flex: 1;
  min-width: 0;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--color-text-tertiary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 16px 20px;
  flex-shrink: 0;
}

.detection-context-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  background: var(--color-accent-glow);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--color-accent-dark);
}

.detection-context-badge .el-button {
  margin-left: auto;
  padding: 0;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: var(--radius-md);
  resize: none;
}

.input-actions {
  flex-shrink: 0;
}

.send-btn {
  height: 40px;
  gap: 6px;
}

.hide-mobile {
  display: inline;
}

@media (max-width: 968px) {
  .knowledge-page {
    padding: 12px;
  }

  .knowledge-container {
    height: calc(100vh - 120px);
    gap: 12px;
    position: relative;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 80%;
    max-width: 320px;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    border-radius: 0;
    z-index: 200;
    padding: 20px 16px;
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-mask {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 199;
  }

  .menu-btn {
    display: flex;
  }

  .chat-main {
    width: 100%;
  }

  .message-item {
    max-width: 90%;
  }

  .hide-mobile {
    display: none;
  }
}

@media (max-width: 480px) {
  .knowledge-page {
    padding: 8px;
  }

  .knowledge-container {
    height: calc(100vh - 100px);
    gap: 8px;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .chat-title {
    font-size: 16px;
  }

  .chat-messages {
    padding: 16px 12px;
    gap: 16px;
  }

  .message-avatar {
    width: 36px;
    height: 36px;
  }

  .message-bubble {
    padding: 12px 14px;
  }

  .chat-input-area {
    padding: 12px;
  }

  .send-btn span {
    display: none;
  }
}
</style>
