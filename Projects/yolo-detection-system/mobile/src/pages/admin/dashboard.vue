<template>
	<view class="admin-page">
		<view class="page-header">
			<view class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</view>
			<text class="header-title">数据看板</text>
			<view class="placeholder"></view>
		</view>

		<view class="read-only-hint">
			<text class="hint-icon">⚠️</text>
			<text class="hint-text">仅查看，编辑请在 Web 端操作</text>
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

			<view v-else class="dashboard-content">
				<view class="stats-grid">
					<view class="stat-card">
						<text class="stat-value">{{ stats.total_users || 0 }}</text>
						<text class="stat-label">用户总数</text>
					</view>
					<view class="stat-card">
						<text class="stat-value">{{ stats.total_detections || 0 }}</text>
						<text class="stat-label">检测总数</text>
					</view>
					<view class="stat-card">
						<text class="stat-value">{{ stats.total_knowledge || 0 }}</text>
						<text class="stat-label">知识总数</text>
					</view>
					<view class="stat-card">
						<text class="stat-value">{{ stats.total_chats || 0 }}</text>
						<text class="stat-label">对话总数</text>
					</view>
				</view>

				<view class="chart-card">
					<text class="card-title">今日概览</text>
					<view class="today-list">
						<view class="today-item">
							<text class="today-value">{{ stats.today_users || 0 }}</text>
							<text class="today-label">新增用户</text>
						</view>
						<view class="today-item">
							<text class="today-value">{{ stats.today_detections || 0 }}</text>
							<text class="today-label">新增检测</text>
						</view>
						<view class="today-item">
							<text class="today-value">{{ stats.today_chats || 0 }}</text>
							<text class="today-label">新增对话</text>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '@/api/admin'

const stats = ref({})
const loading = ref(false)
const refreshing = ref(false)

async function loadStats() {
	loading.value = true
	try {
		const data = await getDashboardStats()
		stats.value = data
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	loadStats()
}

function goBack() {
	uni.navigateBack()
}

onMounted(() => {
	loadStats()
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

.dashboard-content {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 16rpx;
}

.stat-card {
	background: #fff;
	border-radius: 20rpx;
	padding: 24rpx;
	text-align: center;
}

.stat-value {
	font-size: 48rpx;
	font-weight: 700;
	color: #E07A5F;
	display: block;
}

.stat-label {
	font-size: 24rpx;
	color: #999;
	margin-top: 8rpx;
	display: block;
}

.chart-card {
	background: #fff;
	border-radius: 20rpx;
	padding: 24rpx;
}

.card-title {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.today-list {
	display: flex;
	justify-content: space-between;
}

.today-item {
	flex: 1;
	text-align: center;
}

.today-value {
	font-size: 40rpx;
	font-weight: 700;
	color: #E07A5F;
	display: block;
}

.today-label {
	font-size: 24rpx;
	color: #999;
	margin-top: 8rpx;
	display: block;
}
</style>
