<template>
	<view class="history-page">
		<view class="page-header">
			<text class="header-title">检测历史</text>
		</view>

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
				<text class="loading-text">加载中...</text>
			</view>

			<EmptyState v-else-if="records.length === 0" icon="📋" title="暂无检测记录" desc="完成检测后会在这里显示" />

			<view v-else class="record-list">
				<view
					v-for="record in records"
					:key="record.id"
					class="record-item"
					@click="goDetail(record.id)"
				>
					<image :src="getRecordImage(record)" mode="aspectFill" class="record-image" />
					<view class="record-info">
						<text class="record-disease">{{ getDiseaseName(record) }}</text>
						<text class="record-time">{{ formatTime(record.created_at) }}</text>
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
import { ref, onMounted } from 'vue'
import { getHistoryList } from '@/api/history'
import { getFullUrl } from '@/utils/format'
import EmptyState from '@/components/EmptyState.vue'

const records = ref([])
const loading = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = ref(10)
const hasMore = ref(true)

function getRecordImage(record) {
	if (record.result_image) return getFullUrl(record.result_image)
	if (record.original_image) return getFullUrl(record.original_image)
	return ''
}

function getDiseaseName(record) {
	const detections = record.detections || []
	if (detections.length === 0) return '未知病害'
	if (detections.length === 1) return detections[0].class_name
	return detections.map(d => d.class_name).join(', ')
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
		if (isRefresh) {
			records.value = data.items || []
		} else {
			records.value = [...records.value, ...(data.items || [])]
		}
		hasMore.value = (data.items || []).length >= pageSize.value
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
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

onMounted(() => {
	loadRecords()
})
</script>

<style lang="scss" scoped>
.history-page {
	min-height: 100vh;
	background: #F5F5F5;
}

.page-header {
	padding: 28rpx 32rpx;
	background: #E07A5F;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #fff;
}

.history-content {
	height: calc(100vh - 88rpx);
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

.record-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.record-item {
	display: flex;
	align-items: center;
	background: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.record-image {
	width: 140rpx;
	height: 140rpx;
	border-radius: 16rpx;
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
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
}

.record-time {
	font-size: 24rpx;
	color: #999;
}

.record-arrow {
	font-size: 40rpx;
	color: #ccc;
}

.load-more {
	padding: 32rpx;
	text-align: center;
}

.load-more-text {
	font-size: 26rpx;
	color: #999;
}

.no-more {
	padding: 24rpx;
	text-align: center;
}

.no-more-text {
	font-size: 24rpx;
	color: #ccc;
}
</style>
