<template>
	<view class="chat-page">
		<view class="chat-header">
		<view class="header-left">
			<view class="header-icon-wrap">
				<AppIcon name="chat" :size="30" color="#C8442F" />
			</view>
			<view class="header-text">
				<text class="header-title">AI 问答</text>
				<text class="header-subtitle">基于识别结果答疑解惑</text>
			</view>
		</view>
		<view class="header-action" @click="showSessionPanel = !showSessionPanel">
			<AppIcon name="menu" :size="36" color="#FFFFFF" />
			<text class="action-text">会话</text>
		</view>
	</view>

		<view class="session-panel" :class="{ visible: showSessionPanel }" @click.stop>
			<view class="panel-header">
				<view class="panel-header-left">
					<text class="panel-title">历史会话</text>
					<text class="panel-count">{{ sessions.length }} 个</text>
				</view>
				<view class="panel-close" @click="showSessionPanel = false">
					<AppIcon name="close" :size="30" color="#8A938C" />
				</view>
			</view>
			<view class="session-list">
				<view class="new-session" @click="startNewSession">
					<view class="new-icon-wrap">
						<AppIcon name="sparkles" :size="26" color="#FFFFFF" />
					</view>
					<text class="new-text">新建会话</text>
				</view>
				<view
					v-for="session in sessions"
					:key="session.session_id"
					class="session-item"
					:class="{ active: currentSessionId === session.session_id }"
					@click="switchSession(session.session_id)"
				>
					<view class="session-info">
						<text class="session-name">{{ session.title || '未命名会话' }}</text>
						<text class="session-time">{{ formatSessionTime(session.last_time) }}</text>
					</view>
					<view class="session-delete" @click.stop="deleteSession(session.session_id)">
						<AppIcon name="close" :size="28" color="#C3C9C3" />
					</view>
				</view>
			</view>
		</view>

		<scroll-view
			class="chat-content"
			scroll-y
			:scroll-into-view="scrollToId"
			scroll-with-animation
			:show-scrollbar="false"
		>
			<view v-if="contextImage || detectionContext" class="context-image-bar">
				<image v-if="contextImage" :src="contextImage" mode="aspectFit" class="context-img" />
				<text v-if="detectionContext" class="context-label">已带入检测结果：{{ detectionContext }}</text>
				<text v-else class="context-label">检测图片已带入</text>
				<view class="context-close" @click="clearContextImage">
					<AppIcon name="close" :size="32" color="#C3C9C3" />
				</view>
			</view>

			<view v-if="messages.length === 0" class="quick-questions">
				<text class="quick-title">快捷提问</text>
				<view class="quick-list">
				<view
					v-for="(q, idx) in quickQuestions"
					:key="idx"
					class="quick-item"
					@click="sendQuickQuestion(q)"
				>
					<AppIcon name="sparkles" :size="24" color="#C8442F" />
					<text>{{ q }}</text>
				</view>
			</view>
			</view>

			<view v-for="(msg, idx) in messages" :key="idx" :id="'msg-' + idx">
				<ChatBubble :isSelf="msg.role === 'user'" :content="msg.content" :time="formatTime(msg.created_at)" />
				<view v-if="msg.role === 'assistant' && msg.sources && msg.sources.length > 0" class="sources-block">
					<text class="sources-label">参考来源</text>
					<view
						v-for="(source, sidx) in msg.sources"
						:key="sidx"
						class="source-item"
						@click="goSource(source)"
					>
						<text class="source-name">{{ source.title || source.file_name || '来源' }}</text>
						<text class="source-arrow">›</text>
					</view>
				</view>
			</view>

			<view v-if="isThinking" class="thinking-bubble">
				<text class="thinking-text">AI 正在思考...</text>
				<view class="thinking-dots">
					<text class="dot">.</text>
					<text class="dot">.</text>
					<text class="dot">.</text>
				</view>
			</view>
		</scroll-view>

		<view class="chat-input-area">
			<input
				class="input-box"
				v-model="inputText"
				placeholder="输入问题，最多 500 字..."
				maxlength="500"
				:adjust-position="true"
				confirm-type="send"
				@confirm="sendMessage"
			/>
			<button
				class="send-btn"
				:class="{ disabled: !inputText.trim() || isThinking }"
				@click="sendMessage"
			>发送</button>
		</view>

		<view class="mask" :class="{ visible: showSessionPanel }" @click="showSessionPanel = false"></view>
	</view>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { askQuestion, askQuestionStream, getSessionList, getChatHistory, deleteSession as apiDeleteSession } from '@/api/knowledge'
import { showError } from '@/utils/error'
import ChatBubble from '@/components/ChatBubble.vue'
import AppIcon from '@/components/AppIcon.vue'
import { useChatStore } from '@/store/chat'

const chatStore = useChatStore()

const showSessionPanel = ref(false)
const currentSessionId = ref('')
const sessions = ref([])
const messages = ref([])
const inputText = ref('')
const isThinking = ref(false)
const scrollToId = ref('')
const contextImage = ref('')
const detectionContext = ref('')
const detectedClassId = ref(null)
const pageReady = ref(false)

const quickQuestions = ref(['这个病严重吗？', '怎么防治？', '用什么药剂？', '多久能治好？'])

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function formatSessionTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}/${date.getDate()}`
}

let scrollTimer = null

function scrollToBottom() {
	if (scrollTimer) return
	scrollTimer = setTimeout(() => {
		scrollTimer = null
		nextTick(() => {
			const len = messages.value.length
			scrollToId.value = len > 0 ? `msg-${len - 1}` : ''
		})
	}, 50)
}

function typeWriter(msg, fullText) {
	const step = 2
	let index = 0
	msg.content = ''
	return new Promise((resolve) => {
		const timer = setInterval(() => {
			index += step
			msg.content = fullText.slice(0, index)
			if (index >= fullText.length) {
				clearInterval(timer)
				resolve()
			}
		}, 25)
	})
}

function goSource(source) {
	const knowledgeId = source.knowledge_id || source.id
	if (knowledgeId) {
		uni.navigateTo({ url: `/pages/knowledge/detail?id=${knowledgeId}` })
	}
}

function clearContextImage() {
	contextImage.value = ''
	detectionContext.value = ''
	detectedClassId.value = null
}

function getDiseaseName(detection) {
	if (detection?.disease_profile?.disease_name) return detection.disease_profile.disease_name
	return detection?.class_name || ''
}

function applyDetectionContext(detections) {
	const first = detections?.[0]
	if (!first) return
	detectionContext.value = `${getDiseaseName(first)} (${(first.confidence * 100).toFixed(1)}%)`
	detectedClassId.value = first.class_id ?? null
}

function prefillFromDetection(detections) {
	const first = detections?.[0]
	if (!first) return
	const name = getDiseaseName(first)
	if (!name) return
	inputText.value = `${name}怎么防治？`
	quickQuestions.value = [
		`${name}严重吗？`,
		`${name}怎么防治？`,
		`${name}用什么药剂？`,
		`${name}多久能治好？`
	]
}

function applyPendingDetection() {
	const pending = chatStore.pendingDetection
	if (!pending) return
	chatStore.clearPendingDetection()
	if (pending.result_image) {
		contextImage.value = pending.result_image
	}
	const detections = pending.detections || []
	const first = detections[0]
	// 健康叶片不构成病害上下文，只带入图片
	if (!first || first.class_name === '健康叶片') return
	applyDetectionContext(detections)
	prefillFromDetection(detections)
}

async function refreshSessions() {
	try {
		const data = await getSessionList()
		sessions.value = data.sessions || []
	} catch (e) {
		sessions.value = []
	}
}

async function loadSessions() {
	await refreshSessions()
	if (sessions.value.length > 0) {
		await switchSession(sessions.value[0].session_id)
	} else {
		startNewSession()
	}
}

function startNewSession() {
	currentSessionId.value = ''
	messages.value = []
	clearContextImage()
	showSessionPanel.value = false
}

function toMessage(item) {
	return { role: item.role, content: item.content, created_at: item.created_at, sources: item.metadata?.sources }
}

async function switchSession(sessionId) {
	currentSessionId.value = sessionId
	messages.value = []
	clearContextImage()
	showSessionPanel.value = false
	try {
		const data = await getChatHistory(sessionId)
		messages.value = (data.list || []).map(toMessage)
	} catch (e) {
		showError(e, '历史消息加载失败')
	}
	scrollToBottom()
}

async function deleteSession(sessionId) {
	if (sessionId === currentSessionId.value) {
		uni.showToast({ title: '不能删除当前会话', icon: 'none' })
		return
	}
	try {
		await apiDeleteSession(sessionId)
		await refreshSessions()
	} catch (e) {
		showError(e, '删除失败')
	}
}

function sendQuickQuestion(q) {
	inputText.value = q
	sendMessage()
}

function buildAskParams(question) {
	const params = { question, session_id: currentSessionId.value }
	if (detectionContext.value) {
		params.detection_context = detectionContext.value
	}
	if (detectedClassId.value !== null) {
		params.detected_class_id = detectedClassId.value
	}
	return params
}

async function sendMessage() {
	const text = inputText.value.trim()
	if (!text || isThinking.value) return

	const isNewSession = !currentSessionId.value
	isThinking.value = true
	messages.value.push({ role: 'user', content: text, created_at: new Date().toISOString() })
	inputText.value = ''
	scrollToBottom()

	let assistantMsg = null
	const params = buildAskParams(text)

	try {
		const result = await askQuestionStream(params, (part) => {
			if (!part) return
			// 首个增量到达时才建立气泡，让 AI 思考动画先出现
			if (!assistantMsg) {
				assistantMsg = reactive({
					role: 'assistant',
					content: '',
					created_at: new Date().toISOString(),
					sources: []
				})
				messages.value.push(assistantMsg)
				isThinking.value = false
				scrollToBottom()
			}
			assistantMsg.content += part
		})

		if (!assistantMsg) {
			// 平台/中间链路不支持流式时回退普通接口，避免提问重复落库
			const data = await askQuestion(params)
			assistantMsg = reactive({
				role: 'assistant',
				content: '',
				created_at: new Date().toISOString(),
				sources: data.sources || []
			})
			messages.value.push(assistantMsg)
			isThinking.value = false
			await typeWriter(assistantMsg, data.answer)
			currentSessionId.value = data.session_id || currentSessionId.value
		} else {
			currentSessionId.value = result.session_id || currentSessionId.value
			assistantMsg.sources = result.sources || assistantMsg.sources || []
		}

		if (isNewSession) {
			await refreshSessions()
		}
	} catch (e) {
		if (assistantMsg) {
			// 已有部分内容时保留并提示中断，不再重复请求
			assistantMsg.content += '\n\n[回答中断，请重试]'
		} else if (e?.message === 'NO_DELTA') {
			// 无任何流式增量，回退普通接口
			try {
				const data = await askQuestion(params)
				assistantMsg = reactive({
					role: 'assistant',
					content: '',
					created_at: new Date().toISOString(),
					sources: data.sources || []
				})
				messages.value.push(assistantMsg)
				await typeWriter(assistantMsg, data.answer)
				currentSessionId.value = data.session_id || currentSessionId.value
				if (isNewSession) await refreshSessions()
			} catch (e2) {
				messages.value.push({
					role: 'assistant',
					content: '抱歉，AI 暂时无法回答，请稍后重试。',
					created_at: new Date().toISOString()
				})
			}
		} else {
			messages.value.push({
				role: 'assistant',
				content: '抱歉，AI 暂时无法回答，请稍后重试。',
				created_at: new Date().toISOString()
			})
		}
	} finally {
		isThinking.value = false
		scrollToBottom()
	}
}

watch(messages, () => {
	scrollToBottom()
}, { deep: true })

onMounted(async () => {
	await loadSessions()
	// 首次进入：等待会话初始化完成后再消费待带入的检测结果，避免被清空
	applyPendingDetection()
	pageReady.value = true
})

onShow(() => {
	// tabBar 页面二次进入：onShow 先于 onMounted，首次由上面的初始化负责
	if (pageReady.value) {
		applyPendingDetection()
	}
})
</script>

<style lang="scss" scoped>
.chat-page {
	height: 100vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	background: var(--bg-2);
}

.chat-header {
	position: relative;
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: calc(var(--status-bar-height, 0px) + 28rpx) 32rpx 28rpx;
	background: var(--forest);
	overflow: hidden;
}

.chat-header::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-image:
		linear-gradient(rgba(255, 255, 255, 0.04) 1rpx, transparent 1rpx),
		linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1rpx, transparent 1rpx);
	background-size: 44rpx 44rpx;
	pointer-events: none;
}

.header-left {
	position: relative;
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.header-icon-wrap {
	width: 64rpx;
	height: 64rpx;
	border-radius: 20rpx;
	background: rgba(255, 255, 255, 0.12);
	border: 1rpx solid rgba(255, 255, 255, 0.16);
	display: flex;
	align-items: center;
	justify-content: center;
}

.header-text {
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.header-title {
	font-size: 34rpx;
	font-weight: 700;
	color: #fff;
	line-height: 1.2;
}

.header-subtitle {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.7);
}

.header-action {
	position: relative;
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 12rpx 20rpx;
	border-radius: 999rpx;
	background: rgba(255, 255, 255, 0.1);
	border: 1rpx solid rgba(255, 255, 255, 0.14);
}

.action-text {
	font-size: 24rpx;
	font-weight: 600;
	color: #fff;
}

.session-panel {
	position: fixed;
	top: 0;
	left: 0;
	width: 66%;
	height: 100%;
	background: var(--bg-1);
	z-index: 100;
	transform: translateX(-100%);
	transition: transform 0.3s ease;
	box-shadow: 4rpx 0 20rpx rgba(0, 0, 0, 0.1);
}

.session-panel.visible {
	transform: translateX(0);
}

.panel-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 32rpx;
	background: var(--forest);
}

.panel-header-left {
	display: flex;
	align-items: baseline;
	gap: 12rpx;
}

.panel-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #fff;
}

.panel-count {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.6);
}

.panel-close {
	width: 56rpx;
	height: 56rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 16rpx;
	background: rgba(255, 255, 255, 0.1);
}

.session-list {
	padding: 24rpx;
}

.new-session {
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: 24rpx;
	border-radius: 16rpx;
	background: var(--forest-light);
	margin-bottom: 16rpx;
}

.new-icon-wrap {
	width: 56rpx;
	height: 56rpx;
	border-radius: 18rpx;
	background: var(--brand);
	display: flex;
	align-items: center;
	justify-content: center;
}

.new-text {
	font-size: 28rpx;
	color: var(--forest);
	font-weight: 700;
}

.session-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	border-radius: 16rpx;
	margin-bottom: 8rpx;
	position: relative;
	border: 1rpx solid transparent;
}

.session-item.active {
	background: var(--brand-glow);
	border-color: rgba(200, 68, 47, 0.18);
}

.session-item:active {
	background: var(--bg-3);
}

.session-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 6rpx;
	min-width: 0;
	padding-right: 44rpx;
}

.session-name {
	font-size: 26rpx;
	font-weight: 600;
	color: var(--text-1);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.session-item.active .session-name {
	color: var(--brand);
}

.session-time {
	font-size: 22rpx;
	color: var(--text-3);
}

.session-delete {
	position: absolute;
	right: 16rpx;
	width: 48rpx;
	height: 48rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 12rpx;
}

.chat-content {
	flex: 1;
	min-height: 0;
	padding: 24rpx;
	padding-bottom: 120rpx;
}

.context-image-bar {
	position: relative;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 16rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
	box-shadow: var(--shadow-sm);
}

.context-img {
	display: block;
	width: 100%;
	height: 360rpx;
	border-radius: 12rpx;
	background: var(--bg-2);
}

.context-label {
	display: block;
	font-size: 24rpx;
	font-weight: 600;
	color: var(--brand);
	margin-top: 12rpx;
	text-align: center;
}

.context-close {
	position: absolute;
	top: 12rpx;
	right: 12rpx;
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	background: rgba(0, 0, 0, 0.55);
	display: flex;
	align-items: center;
	justify-content: center;
}

.quick-questions {
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 24rpx;
	padding: 28rpx;
	margin-bottom: 20rpx;
	box-shadow: var(--shadow-sm);
}

.quick-title {
	font-size: 28rpx;
	font-weight: 700;
	color: var(--text-1);
	margin-bottom: 16rpx;
	display: block;
}

.quick-list {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.quick-item {
	display: flex;
	align-items: center;
	gap: 8rpx;
	background: var(--brand-glow);
	color: var(--brand);
	font-size: 26rpx;
	font-weight: 600;
	padding: 12rpx 24rpx;
	border-radius: 20rpx;
}

.thinking-bubble {
	display: flex;
	align-items: center;
	gap: 8rpx;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	padding: 20rpx 24rpx;
	border-radius: 22rpx 22rpx 22rpx 8rpx;
	margin-bottom: 20rpx;
}

.thinking-bubble::before {
	content: '';
	width: 12rpx;
	height: 12rpx;
	border-radius: 50%;
	background: var(--brand);
	flex-shrink: 0;
}

.sources-block {
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 16rpx;
	padding: 16rpx 20rpx;
	margin: 0 0 20rpx 64rpx;
}

.sources-label {
	font-size: 24rpx;
	color: var(--text-3);
	margin-bottom: 12rpx;
	display: block;
}

.source-item {
	display: flex;
	align-items: center;
	padding: 12rpx 0;
	border-bottom: 1rpx solid var(--border-light);
}

.source-item:last-child {
	border-bottom: none;
}

.source-name {
	flex: 1;
	font-size: 26rpx;
	color: var(--brand);
}

.source-arrow {
	font-size: 32rpx;
	color: var(--text-disabled);
}

.thinking-text {
	font-size: 26rpx;
	color: var(--text-2);
}

.thinking-dots {
	display: flex;
	gap: 4rpx;
}

.dot {
	font-size: 24rpx;
	color: var(--text-3);
	animation: blink 1s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
	0%, 100% { opacity: 0.3; }
	50% { opacity: 1; }
}

.chat-input-area {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: 16rpx 24rpx;
	padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
	background: var(--bg-1);
	border-top: 1rpx solid var(--border-light);
}

.input-box {
	flex: 1;
	height: 84rpx;
	background: var(--bg-2);
	border: 1rpx solid var(--border-light);
	border-radius: 24rpx;
	padding: 0 28rpx;
	font-size: 28rpx;
}

.send-btn {
	height: 84rpx;
	padding: 0 40rpx;
	border-radius: 24rpx;
	background: var(--brand);
	box-shadow: var(--shadow-brand);
	color: #fff;
	font-size: 28rpx;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
}

.send-btn.disabled {
	opacity: 0.4;
	box-shadow: none;
}

.send-btn::after {
	border: none;
}

.mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	z-index: 99;
	opacity: 0;
	pointer-events: none;
	transition: opacity 0.3s ease;
}

.mask.visible {
	opacity: 1;
	pointer-events: auto;
}
</style>
