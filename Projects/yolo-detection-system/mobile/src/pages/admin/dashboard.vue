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
						<text class="stat-value">{{ stats.pending_count || 0 }}</text>
						<text class="stat-label">待审核</text>
					</view>
				</view>

				<view class="chart-card">
					<text class="card-title">病害检测统计</text>
					<view class="bar-chart">
						<view
							v-for="item in detectionStats"
							:key="item.name"
							class="bar-item"
						>
							<text class="bar-name">{{ item.name }}</text>
							<view class="bar-track">
								<view
									class="bar-fill"
									:style="{ width: getBarWidth(item.count) + '%' }"
								></view>
							</view>
							<text class="bar-count">{{ item.count }}</text>
						</view>
					</view>
				</view>

				<view class="chart-card">
					<text class="card-title">检测趋势（近7天）</text>
					<view class="line-chart">
						<view
							v-for="(item, idx) in trendStats"
							:key="idx"
							class="line-item"
						>
							<view class="line-bar">
								<view
									class="line-fill"
									:style="{ height: getLineHeight(item.count) + '%' }"
								></view>
							</view>
							<text class="line-label">{{ item.date }}</text>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getAdminDashboard } from '@/api/admin'

const stats = ref({})
const loading = ref(false)
const refreshing = ref(false)

const detectionStats = computed(() => {
	return stats.value.detection_stats || [
		{ name: '健康', count: 0 },
		{ name: '早疫病', count: 0 },
		{ name: '晚疫病', count: 0 },
		{ name: '叶霉病', count: 0 },
		{ name: '斑枯病', count: 0 },
		{ name: '灰霉病', count: 0 }
	]
})

const trendStats = computed(() => {
	return stats.value.daily_trend || [
		{ date: '周一', count: 0 },
		{ date: '周二', count: 0 },
		{ date: '周三', count: 0 },
		{ date: '周四', count: 0 },
		{ date: '周五', count: 0 },
		{ date: '周六', count: 0 },
		{ date: '周日', count: 0 }
	]
})

function getBarWidth(count) {
	const max = Math.max(...detectionStats.value.map(d => d.count), 1)
	return (count / max) * 100
}

function getLineHeight(count) {
	const max = Math.max(...trendStats.value.map(d => d.count), 1)
	return (count / max) * 100
}

async function loadStats() {
	loading.value = true
	try {
		const data = await getAdminDashboard()
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

.bar-chart {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.bar-item {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.bar-name {
	width: 80rpx;
	font-size: 24rpx;
	color: #666;
	flex-shrink: 0;
}

.bar-track {
	flex: 1;
	height: 24rpx;
	background: #F5F5F5;
	border-radius: 12rpx;
	overflow: hidden;
}

.bar-fill {
	height: 100%;
	background: linear-gradient(90deg, #E07A5F 0%, #C96247 100%);
	border-radius: 12rpx;
	transition: width 0.5s ease;
}

.bar-count {
	width: 60rpx;
	font-size: 24rpx;
	color: #999;
	text-align: right;
	flex-shrink: 0;
}

.line-chart {
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
	height: 200rpx;
	padding-top: 20rpx;
}

.line-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	flex: 1;
	height: 100%;
}

.line-bar {
	width: 32rpx;
	height: 100%;
	background: #F5F5F5;
	border-radius: 16rpx;
	display: flex;
	align-items: flex-end;
	overflow: hidden;
}

.line-fill {
	width: 100%;
	background: linear-gradient(180deg, #E07A5F 0%, #C96247 100%);
	border-radius: 16rpx;
	transition: height 0.5s ease;
}

.line-label {
	font-size: 22rpx;
	color: #999;
	margin-top: 12rpx;
}
</style>
