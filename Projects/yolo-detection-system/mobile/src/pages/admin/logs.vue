<template>
	<view class="admin-page">
		<view class="page-header">
			<view class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</view>
			<text class="header-title">操作日志</text>
			<view class="placeholder"></view>
		</view>

		<view class="read-only-hint">
			<text class="hint-icon">⚠️</text>
			<text class="hint-text">仅查看，无操作权限</text>
		</view>

		<scroll-view
			class="content"
			scroll-y
			@refresherrefresh="onRefresh"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
			:show-scrollbar="false"
		>
			<view v-if="loading && !refreshing" class="loading-row">
				<text class="loading-text">加载中...</text>
			</view>

			<EmptyState v-else-if="logs.length === 0" icon="📜" title="暂无日志" />

			<view v-else class="log-list">
				<view
					v-for="log in logs"
					:key="log.id"
					class="log-item"
				>
					<view class="log-header">
						<text class="log-user">{{ log.username || '未知用户' }}</text>
						<text class="log-time">{{ formatTime(log.created_at) }}</text>
					</view>
					<text class="log-action">{{ log.action }}</text>
					<text class="log-detail">{{ log.detail || '-' }}</text>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminLogs } from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'

const logs = ref([])
const loading = ref(false)
const refreshing = ref(false)

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

async function loadLogs() {
	loading.value = true
	try {
		const data = await getAdminLogs()
		logs.value = data.items || []
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	loadLogs()
}

function goBack() {
	uni.navigateBack()
}

onMounted(() => {
	loadLogs()
})
</script>

<style lang="scss" scoped>
.admin-page {
	min-height: 100vh;
	background: #F5F5F5;
}

.page-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 32rpx;
	background: #E07A5F;
}

.back-btn {
	width: 64rpx;
	height: 64rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.back-icon {
	font-size: 48rpx;
	color: #fff;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #fff;
}

.placeholder {
	width: 64rpx;
}

.read-only-hint {
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 16rpx 24rpx;
	background: rgba(255, 152, 0, 0.1);
}

.hint-icon {
	font-size: 28rpx;
}

.hint-text {
	font-size: 24rpx;
	color: #FF9800;
}

.content {
	height: calc(100vh - 180rpx);
	padding: 24rpx;
}

.loading-row {
	padding: 60rpx;
	text-align: center;
}

.loading-text {
	font-size: 28rpx;
	color: #999;
}

.log-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.log-item {
	background: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
}

.log-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 12rpx;
}

.log-user {
	font-size: 28rpx;
	font-weight: 600;
	color: #333;
}

.log-time {
	font-size: 24rpx;
	color: #999;
}

.log-action {
	font-size: 26rpx;
	color: #E07A5F;
	margin-bottom: 8rpx;
	display: block;
}

.log-detail {
	font-size: 24rpx;
	color: #666;
}
</style>
