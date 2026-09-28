<template>
	<view class="history-page">
		<PageHeader
			title="检测历史"
			subtitle="全部检测记录都在这里"
			eyebrow="DETECTION ARCHIVE"
		/>

		<scroll-view
			class="history-content"
			scroll-y
			@refresherrefresh="onRefresh"
			@scrolltolower="onLoadMore"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
			:show-scrollbar="false"
		>
			<view v-if="loading && !refreshing" class="loading-row">
				<view class="skeleton-item"></view>
				<view class="skeleton-item"></view>
				<view class="skeleton-item"></view>
			</view>

			<EmptyState v-else-if="records.length === 0" name="clipboard" title="暂无检测记录" desc="完成检测后会在这里显示" />

			<view v-else class="record-list">
				<view
					v-for="record in records"
					:key="record.id"
					class="record-item"
					@click="goDetail(record.id)"
				>
					<image
						v-if="getRecordImage(record) && !isImageBroken(record.id)"
						:src="getRecordImage(record)"
						mode="aspectFill"
						class="record-image"
						@error="onImageError(record.id)"
					/>
					<view v-else class="record-image image-broken">
						<AppIcon name="leaf" :size="30" color="#C3C9C3" />
					</view>
					<view class="record-info">
						<text class="record-disease">{{ getDiseaseName(record) }}</text>
						<text class="record-time">{{ formatTime(record.created_at) }}</text>
					</view>
					<view class="record-status" :class="{ healthy: isHealthyRecord(record) }">
						<text class="status-text">{{ getStatusLabel(record) }}</text>
					</view>
					<text class="record-arrow">›</text>
				</view>
			</view>

			<view v-if="hasMore && !loading" class="load-more">
				<text class="load-more-text">加载更多...</text>
			</view>
			<view v-if="!hasMore && records.length > 0" class="no-more">
				<text class="no-more-text">- 已加载全部 -</text>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getHistoryList } from '@/api/history'
import { getFullUrl } from '@/utils/format'
import { showError } from '@/utils/error'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'

const records = ref([])
const loading = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = ref(10)
const hasMore = ref(true)
const brokenImages = ref([])

function isImageBroken(id) {
	return brokenImages.value.includes(id)
}

function onImageError(id) {
	if (!brokenImages.value.includes(id)) {
		brokenImages.value = [...brokenImages.value, id]
	}
}

function getRecordImage(record) {
	const path = record.result_path || record.original_path
	return path ? getFullUrl(path) : ''
}

function getDiseaseName(record) {
	const detections = record.detections || []
	if (detections.length === 0) return record.original_filename || '未知病害'
	if (detections.length === 1) return detections[0].class_name
	return detections.map(d => d.class_name).join(', ')
}

function isHealthyRecord(record) {
	const detections = record.detections || []
	return detections.length > 0 && detections.every(d => d.class_name === '健康叶片')
}

function getStatusLabel(record) {
	const detections = record.detections || []
	if (detections.length === 0) return '待查看'
	if (detections.every(d => d.class_name === '健康叶片')) return '健康'
	return '需关注'
}

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

async function loadRecords(isRefresh = false) {
	if (loading.value) return

	loading.value = true
	try {
		const data = await getHistoryList({ page: page.value, page_size: pageSize.value })
		const items = data.list || []
		if (isRefresh) {
			records.value = items
			brokenImages.value = []
		} else {
			records.value = [...records.value, ...items]
		}
		hasMore.value = items.length >= pageSize.value
	} catch (e) {
		showError(e, '加载失败')
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	page.value = 1
	hasMore.value = true
	loadRecords(true)
}

function onLoadMore() {
	if (hasMore.value && !loading.value) {
		page.value++
		loadRecords()
	}
}

function goDetail(id) {
	uni.navigateTo({ url: `/pages/history/detail?id=${id}` })
}

onShow(() => {
	page.value = 1
	hasMore.value = true
	loadRecords(true)
})
</script>

<style lang="scss" scoped>
.history-page {
	height: 100vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	background: var(--bg-2);
}

.history-page :deep(.page-header) {
	flex-shrink: 0;
}

.history-content {
	flex: 1;
	min-height: 0;
	padding: 24rpx;
}

.loading-row {
	padding: 60rpx 0;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.skeleton-item {
	height: 180rpx;
	border-radius: 20rpx;
	background: linear-gradient(100deg, var(--bg-3) 40%, var(--bg-1) 50%, var(--bg-3) 60%);
	background-size: 200% 100%;
	animation: skeleton-shimmer 1.6s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
	0% {
		background-position: 100% 0;
	}
	100% {
		background-position: -100% 0;
	}
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
	border: 1rpx solid var(--border-light);
	box-shadow: 0 2rpx 12rpx rgba(31, 36, 33, 0.05);
}

.record-image {
	width: 140rpx;
	height: 140rpx;
	border-radius: 16rpx;
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--bg-2);
}

.record-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
	padding: 0 20rpx;
}

.record-disease {
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-1);
}

.record-time {
	font-size: 24rpx;
	color: var(--text-3);
}

.record-status {
	flex-shrink: 0;
	padding: 6rpx 16rpx;
	border-radius: 999rpx;
	background: var(--brand-glow);
}

.record-status .status-text {
	font-size: 22rpx;
	font-weight: 600;
	color: var(--brand);
}

.record-status.healthy {
	background: var(--forest-light);
}

.record-status.healthy .status-text {
	color: var(--forest-2);
}

.record-arrow {
	font-size: 40rpx;
	color: var(--text-disabled);
	margin-left: 16rpx;
}

.load-more {
	padding: 32rpx;
	text-align: center;
}

.load-more-text {
	font-size: 26rpx;
	color: var(--text-3);
}

.no-more {
	padding: 24rpx;
	text-align: center;
}

.no-more-text {
	font-size: 24rpx;
	color: var(--text-disabled);
}
</style>
