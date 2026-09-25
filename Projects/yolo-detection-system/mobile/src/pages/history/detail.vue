<template>
	<view class="history-detail-page">
		<LoadingOverlay :visible="loading" text="加载中..." />

		<view v-if="record" class="content">
			<view class="page-header">
				<view class="back-btn" @click="goBack">
					<text class="back-icon">‹</text>
				</view>
				<text class="header-title">检测详情</text>
				<view class="placeholder"></view>
			</view>

			<view class="image-section">
				<view class="image-card">
					<text class="card-label">原图</text>
					<image :src="getFullUrl(record.original_path)" mode="widthFix" class="detail-image" @click="previewImage(record.original_path)" />
				</view>
				<view class="image-card">
					<text class="card-label">检测结果图</text>
					<image :src="getFullUrl(record.result_path)" mode="widthFix" class="detail-image" @click="previewImage(record.result_path)" />
				</view>
			</view>

			<view class="info-section">
				<view class="info-row">
					<text class="info-label">检测时间</text>
					<text class="info-value">{{ formatTime(record.created_at) }}</text>
				</view>
				<view class="info-row">
					<text class="info-label">检测目标数</text>
					<text class="info-value">{{ record.detection_count || 0 }}</text>
				</view>
				<view class="info-row">
					<text class="info-label">模型版本</text>
					<text class="info-value">{{ record.model_version || '-' }}</text>
				</view>
			</view>

			<view class="detection-section">
				<text class="section-title">检测结果</text>
				<view
					v-for="(item, index) in detections"
					:key="index"
					class="detection-item"
				>
					<view class="item-header">
						<text class="item-index">{{ index + 1 }}</text>
						<text
							class="item-tag"
							:class="{ healthy: item.class_name === 'Healthy' }"
						>{{ item.class_name }}</text>
						<text class="item-confidence">{{ (item.confidence * 100).toFixed(1) }}%</text>
					</view>
					<view class="confidence-bar">
						<view
							class="confidence-fill"
							:style="{ width: (item.confidence * 100) + '%' }"
							:class="{ healthy: item.class_name === 'Healthy' }"
						></view>
					</view>
					<DiseaseCard
						v-if="item.disease_profile"
						:profile="item.disease_profile"
						:class-id="item.class_id"
					/>
				</view>
			</view>
		</view>

		<EmptyState v-else-if="!loading" icon="📭" title="记录不存在" />
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getHistoryDetail } from '@/api/history'
import { getFullUrl } from '@/utils/format'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import EmptyState from '@/components/EmptyState.vue'
import DiseaseCard from '@/components/DiseaseCard.vue'

const loading = ref(true)
const record = ref(null)

const detections = computed(() => record.value?.detection_result?.detections || [])

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function previewImage(path) {
	uni.previewImage({
		current: getFullUrl(path),
		urls: [getFullUrl(record.value?.original_path), getFullUrl(record.value?.result_path)].filter(Boolean)
	})
}

function goBack() {
	uni.navigateBack()
}

async function loadRecord() {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const id = currentPage.options?.id

	if (!id) {
		loading.value = false
		return
	}

	try {
		record.value = await getHistoryDetail(id)
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	loadRecord()
})
</script>

<style lang="scss" scoped>
.history-detail-page {
	min-height: 100vh;
	background: #F5F5F5;
}

.content {
	padding-bottom: 40rpx;
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

.image-section {
	padding: 24rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.image-card {
	background: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
}

.card-label {
	font-size: 26rpx;
	color: #999;
	margin-bottom: 12rpx;
	display: block;
}

.detail-image {
	width: 100%;
	border-radius: 12rpx;
}

.info-section {
	background: #fff;
	margin: 0 24rpx;
	border-radius: 20rpx;
	padding: 24rpx;
}

.info-row {
	display: flex;
	justify-content: space-between;
	padding: 16rpx 0;
	border-bottom: 1rpx solid #f5f5f5;
}

.info-row:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #666;
}

.info-value {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.detection-section {
	background: #fff;
	margin: 24rpx;
	border-radius: 20rpx;
	padding: 24rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.detection-item {
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f5f5f5;
}

.detection-item:last-child {
	border-bottom: none;
}

.item-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 12rpx;
}

.item-index {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: rgba(224, 122, 95, 0.1);
	color: #E07A5F;
	font-size: 24rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
}

.item-tag {
	font-size: 28rpx;
	font-weight: 600;
	color: #F44336;
	background: rgba(244, 67, 54, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.item-tag.healthy {
	color: #E07A5F;
	background: rgba(224, 122, 95, 0.1);
}

.item-confidence {
	margin-left: auto;
	font-size: 28rpx;
	font-weight: 600;
	color: #333;
}

.confidence-bar {
	height: 8rpx;
	background: #f0f0f0;
	border-radius: 4rpx;
	overflow: hidden;
	margin-bottom: 20rpx;
}

.confidence-fill {
	height: 100%;
	border-radius: 4rpx;
	background: linear-gradient(90deg, #F44336 0%, #FF9800 50%, #E07A5F 100%);
	transition: width 0.5s ease;
}

.confidence-fill.healthy {
	background: #E07A5F;
}
</style>
