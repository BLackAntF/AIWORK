<template>
	<view class="home-page">
		<!-- 顶部欢迎区 -->
		<view class="header-section">
			<view class="header-bg"></view>
			<view class="header-content">
				<view class="user-info">
					<view class="avatar">{{ avatarText }}</view>
					<view class="user-text">
						<text class="greeting">你好</text>
						<text class="username">{{ displayName }}</text>
					</view>
				</view>
				<text class="header-tip">番茄叶片病害智能诊断平台</text>
			</view>
		</view>

		<!-- 快速操作区 -->
		<view class="quick-section">
			<view class="quick-card detect-card" @click="goDetect">
				<AppIcon class="card-icon" name="camera" :size="56" color="#E07A5F" />
				<view class="card-text">
					<text class="card-title">拍照检测</text>
					<text class="card-desc">拍摄叶片识别病害</text>
				</view>
				<text class="card-arrow">›</text>
			</view>
			<view class="quick-card chat-card" @click="goChat">
				<AppIcon class="card-icon" name="chat" :size="56" color="#E07A5F" />
				<view class="card-text">
					<text class="card-title">AI 问答</text>
					<text class="card-desc">智能咨询病害防治</text>
				</view>
				<text class="card-arrow">›</text>
			</view>
		</view>

		<!-- 最近检测 -->
		<view class="recent-section">
			<view class="section-header">
				<text class="section-title">最近检测</text>
				<text class="view-all" @click="goHistory">查看全部</text>
			</view>

			<view v-if="loading" class="loading-row">
				<text class="loading-text">加载中...</text>
			</view>

			<EmptyState
				v-else-if="records.length === 0"
				name="inbox"
				title="暂无检测记录"
				desc="点击上方'拍照检测'开始"
			/>

			<view v-else class="record-list">
				<view
					v-for="record in records"
					:key="record.id"
					class="record-item"
					@click="goHistoryDetail(record.id)"
				>
					<image :src="getRecordImage(record)" mode="aspectFill" class="record-image" />
					<view class="record-info">
						<text class="record-disease">{{ getDiseaseName(record) }}</text>
						<text class="record-time">{{ formatTime(record.created_at) }}</text>
					</view>
					<text class="record-arrow">›</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { getHistoryList } from '@/api/history'
import { getFullUrl } from '@/utils/format'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'

const userStore = useUserStore()
const loading = ref(false)
const records = ref([])

const displayName = computed(() => userStore.userInfo?.username || '用户')
const avatarText = computed(() => {
	const name = userStore.userInfo?.username || 'U'
	return name.charAt(0).toUpperCase()
})

function getRecordImage(record) {
	const path = record.result_path || record.original_path
	return path ? getFullUrl(path) : ''
}

function getDiseaseName(record) {
	const detections = record.detections || []
	if (detections.length === 0) {
		return record.original_filename || '未知病害'
	}
	if (detections.length === 1) {
		return detections[0].class_name
	}
	return detections.map(d => d.class_name).join(', ')
}

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	const now = new Date()
	const diff = now.getTime() - date.getTime()
	const days = Math.floor(diff / (1000 * 60 * 60 * 24))
	if (days === 0) {
		const hours = Math.floor(diff / (1000 * 60 * 60))
		if (hours === 0) {
			const minutes = Math.floor(diff / (1000 * 60))
			return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
		}
		return `${hours}小时前`
	}
	if (days === 1) return '昨天'
	if (days < 7) return `${days}天前`
	return `${date.getMonth() + 1}/${date.getDate()}`
}

async function loadRecords() {
	loading.value = true
	try {
		const data = await getHistoryList({ page: 1, page_size: 5 })
		records.value = data.list || []
	} catch (e) {
		// 静默失败，显示空状态
	} finally {
		loading.value = false
		uni.stopPullDownRefresh()
	}
}

onPullDownRefresh(() => {
	loadRecords()
})

function goDetect() {
	uni.switchTab({ url: '/pages/detect/index' })
}

function goChat() {
	uni.switchTab({ url: '/pages/chat/index' })
}

function goHistory() {
	uni.switchTab({ url: '/pages/history/index' })
}

function goHistoryDetail(id) {
	uni.navigateTo({ url: `/pages/history/detail?id=${id}` })
}

onMounted(() => {
	if (userStore.token && !userStore.userInfo) {
		userStore.fetchUserInfo().catch(() => {})
	}
	loadRecords()
})
</script>

<style lang="scss" scoped>
.home-page {
	min-height: 100vh;
	padding-bottom: 40rpx;
}

/* 顶部欢迎区 */
.header-section {
	position: relative;
	overflow: hidden;
}

.header-bg {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 360rpx;
	background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
	border-radius: 0 0 48rpx 48rpx;
}

.header-content {
	position: relative;
	padding: 60rpx 40rpx 80rpx;
	z-index: 2;
}

.user-info {
	display: flex;
	align-items: center;
	margin-bottom: 24rpx;
}

.avatar {
	width: 96rpx;
	height: 96rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 40rpx;
	font-weight: 600;
	color: #fff;
	margin-right: 24rpx;
}

.user-text {
	display: flex;
	flex-direction: column;
}

.greeting {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.85);
}

.username {
	font-size: 36rpx;
	font-weight: 600;
	color: #fff;
}

.header-tip {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

/* 快速操作区 */
.quick-section {
	padding: 0 32rpx;
	margin-top: -40rpx;
	position: relative;
	z-index: 3;
}

.quick-card {
	display: flex;
	align-items: center;
	background: var(--bg-1);
	border-radius: 24rpx;
	padding: 32rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.card-icon {
	font-size: 56rpx;
	margin-right: 24rpx;
}

.card-text {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.card-title {
	font-size: 32rpx;
	font-weight: 600;
	color: var(--text-1);
	margin-bottom: 6rpx;
}

.card-desc {
	font-size: 24rpx;
	color: var(--text-3);
}

.card-arrow {
	font-size: 40rpx;
	color: var(--text-disabled);
}

/* 最近检测 */
.recent-section {
	padding: 40rpx 32rpx;
}

.section-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 24rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: var(--text-1);
}

.view-all {
	font-size: 26rpx;
	color: var(--brand);
}

.loading-row {
	padding: 40rpx;
	text-align: center;
}

.loading-text {
	font-size: 26rpx;
	color: var(--text-3);
}

.record-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.record-item {
	display: flex;
	align-items: center;
	background: var(--bg-1);
	border-radius: 20rpx;
	padding: 20rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.record-image {
	width: 120rpx;
	height: 120rpx;
	border-radius: 12rpx;
	flex-shrink: 0;
}

.record-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
	padding: 0 20rpx;
}

.record-disease {
	font-size: 28rpx;
	font-weight: 600;
	color: var(--text-1);
}

.record-time {
	font-size: 24rpx;
	color: var(--text-3);
}

.record-arrow {
	font-size: 36rpx;
	color: var(--text-disabled);
}

.empty-placeholder {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 80rpx 0;
}

.empty-text {
	font-size: 28rpx;
	color: var(--text-3);
	margin-bottom: 12rpx;
}

.empty-sub {
	font-size: 24rpx;
	color: var(--text-disabled);
}
</style>
