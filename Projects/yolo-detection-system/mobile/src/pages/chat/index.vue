<template>
	<view class="chat-page">
		<view class="chat-header">
			<text class="header-title">AI 问答</text>
			<view class="header-action" @click="showSessionPanel = !showSessionPanel">
				<text class="action-icon">☰</text>
				<text class="action-text">会话</text>
			</view>
		</view>

		<view class="session-panel" :class="{ visible: showSessionPanel }" @click.stop>
			<view class="panel-header">
				<text class="panel-title">历史会话</text>
				<view class="panel-close" @click="showSessionPanel = false">✕</view>
			</view>
			<view class="session-list">
				<view class="new-session" @click="startNewSession">
					<text class="new-icon">+</text>
					<text class="new-text">新建会话</text>
				</view>
				<view
					v-for="session in sessions"
					:key="session.session_id"
					class="session-item"
					:class="{ active: currentSessionId === session.session_id }"
					@click="switchSession(session.session_id)"
				>
					<text class="session-name">{{ session.title || '未命名会话' }}</text>
					<text class="session-time">{{ formatSessionTime(session.last_time) }}</text>
					<view class="session-delete" @click.stop="deleteSession(session.session_id)">
						<text>✕</text>
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
			<view v-if="contextImage" class="context-image-bar">
				<image :src="contextImage" mode="widthFix" class="context-img" />
				<text class="context-label">检测图片已带入</text>
				<view class="context-close" @click="clearContextImage">✕</view>
			</view>

			<view v-if="messages.length === 0" class="quick-questions">
				<text class="quick-title">快捷提问</text>
				<view class="quick-list">
					<view
						v-for="(q, idx) in quickQuestions"
						:key="idx"
						class="quick-item"
						@click="sendQuickQuestion(q)"
					>{{ q }}</view>
				</view>
			</view>

			<view v-for="(msg, idx) in messages" :key="idx" :id="'msg-' + idx">
					<ChatBubble :isSelf="msg.role === 'user'" :content="msg.content" :time="formatTime(msg.created_at)" />
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
import { ref, onMounted, nextTick, watch } from 'vue'
import { askQuestion, getSessionList, getChatHistory, deleteSession as apiDeleteSession } from '@/api/knowledge'
import ChatBubble from '@/components/ChatBubble.vue'

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

const quickQuestions = ['这个病严重吗？', '怎么防治？', '用什么药剂？', '多久能治好？']

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

function scrollToBottom() {
	nextTick(() => {
		const len = messages.value.length
		scrollToId.value = len > 0 ? `msg-${len - 1}` : ''
	})
}

function clearContextImage() {
	contextImage.value = ''
	detectionContext.value = ''
	detectedClassId.value = null
}

function applyDetectionContext(detections) {
	const first = detections?.[0]
	if (!first) return
	detectionContext.value = `${first.class_name} (${(first.confidence * 100).toFixed(1)}%)`
	detectedClassId.value = first.class_id ?? null
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
	return { role: item.role, content: item.content, created_at: item.created_at }
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
		uni.showToast({ title: '历史消息加载失败', icon: 'none' })
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
		uni.showToast({ title: '删除失败', icon: 'none' })
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

	try {
		const data = await askQuestion(buildAskParams(text))
		currentSessionId.value = data.session_id || currentSessionId.value
		messages.value.push({
			role: 'assistant',
			content: data.answer,
			created_at: new Date().toISOString()
		})
		if (isNewSession) {
			await refreshSessions()
		}
	} catch (e) {
		messages.value.push({
			role: 'assistant',
			content: '抱歉，AI 暂时无法回答，请稍后重试。',
			created_at: new Date().toISOString()
		})
	} finally {
		isThinking.value = false
		scrollToBottom()
	}
}

watch(messages, () => {
	scrollToBottom()
}, { deep: true })

onMounted(() => {
	uni.$on('detect-to-chat', (data) => {
		if (data?.result_image) {
			contextImage.value = data.result_image
		}
		applyDetectionContext(data?.detections)
	})

	loadSessions()
})
</script>

<style lang="scss" scoped>
.chat-page {
	min-height: 100vh;
	display: flex;
	flex-direction: column;
	background: #F5F5F5;
}

.chat-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 32rpx;
	background: #E07A5F;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #fff;
}

.header-action {
	display: flex;
	align-items: center;
	gap: 8rpx;
}

.action-icon {
	font-size: 28rpx;
	color: #fff;
}

.action-text {
	font-size: 26rpx;
	color: #fff;
}

.session-panel {
	position: fixed;
	top: 0;
	left: 0;
	width: 60%;
	height: 100%;
	background: #fff;
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
	border-bottom: 1rpx solid #f0f0f0;
	background: #E07A5F;
}

.panel-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #fff;
}

.panel-close {
	width: 48rpx;
	height: 48rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
	font-size: 28rpx;
}

.session-list {
	padding: 16rpx;
}

.new-session {
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 24rpx;
	border-radius: 16rpx;
	background: rgba(224, 122, 95, 0.1);
	margin-bottom: 12rpx;
}

.new-icon {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #E07A5F;
	color: #fff;
	font-size: 28rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.new-text {
	font-size: 28rpx;
	color: #E07A5F;
	font-weight: 500;
}

.session-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	border-radius: 12rpx;
	margin-bottom: 8rpx;
	position: relative;
}

.session-item.active {
	background: rgba(224, 122, 95, 0.1);
}

.session-name {
	flex: 1;
	font-size: 26rpx;
	color: #333;
}

.session-time {
	font-size: 22rpx;
	color: #999;
	margin-right: 32rpx;
}

.session-delete {
	position: absolute;
	right: 16rpx;
	width: 36rpx;
	height: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #ccc;
	font-size: 24rpx;
}

.chat-content {
	flex: 1;
	padding: 24rpx;
	padding-bottom: 120rpx;
}

.context-image-bar {
	position: relative;
	background: #fff;
	border-radius: 16rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
}

.context-img {
	width: 100%;
	border-radius: 12rpx;
}

.context-label {
	display: block;
	font-size: 24rpx;
	color: #E07A5F;
	margin-top: 12rpx;
	text-align: center;
}

.context-close {
	position: absolute;
	top: 12rpx;
	right: 12rpx;
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: rgba(0, 0, 0, 0.5);
	color: #fff;
	font-size: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.quick-questions {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
}

.quick-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 16rpx;
	display: block;
}

.quick-list {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.quick-item {
	background: rgba(224, 122, 95, 0.1);
	color: #E07A5F;
	font-size: 26rpx;
	padding: 12rpx 24rpx;
	border-radius: 20rpx;
}

.thinking-bubble {
	display: flex;
	align-items: center;
	gap: 8rpx;
	background: #fff;
	padding: 20rpx 24rpx;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
}

.thinking-text {
	font-size: 26rpx;
	color: #666;
}

.thinking-dots {
	display: flex;
	gap: 4rpx;
}

.dot {
	font-size: 24rpx;
	color: #999;
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
	background: #fff;
	box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.input-box {
	flex: 1;
	height: 80rpx;
	background: #F5F5F5;
	border-radius: 40rpx;
	padding: 0 28rpx;
	font-size: 28rpx;
}

.send-btn {
	height: 80rpx;
	padding: 0 40rpx;
	border-radius: 40rpx;
	background: #E07A5F;
	color: #fff;
	font-size: 28rpx;
	font-weight: 600;
}

.send-btn.disabled {
	opacity: 0.5;
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
