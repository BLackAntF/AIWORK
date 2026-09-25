<template>
	<view class="admin-page">
		<PageHeader title="操作日志" :show-back="true" />

		<view class="read-only-hint">
			<AppIcon name="alert" :size="28" color="#FAAD14" />
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

			<EmptyState v-else-if="logs.length === 0" name="log" title="暂无日志" />

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
import { getLogs } from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'

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
		const data = await getLogs()
		logs.value = data.logs || []
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

onMounted(() => {
	loadLogs()
})
</script>

<style lang="scss" scoped>
.admin-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.read-only-hint {
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 16rpx 24rpx;
	background: rgba(250, 173, 20, 0.1);
}

.hint-text {
	font-size: 24rpx;
	color: var(--warning);
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
	color: var(--text-3);
}

.log-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.log-item {
	background: var(--bg-1);
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
	color: var(--text-1);
}

.log-time {
	font-size: 24rpx;
	color: var(--text-3);
}

.log-action {
	font-size: 26rpx;
	color: var(--brand);
	margin-bottom: 8rpx;
	display: block;
}

.log-detail {
	font-size: 24rpx;
	color: var(--text-2);
}
</style>
