<template>
	<view class="history-detail-page">
		<LoadingOverlay :visible="loading" text="加载中..." />

		<view v-if="record" class="content">
			<PageHeader title="检测详情" subtitle="原始影像与识别结果" eyebrow="DETECTION REPORT" :show-back="true" />

			<view class="image-section">
				<view class="image-card">
					<text class="card-label">原图</text>
					<image
						v-if="getFullUrl(record.original_path) && !originalImageBroken"
						:src="getFullUrl(record.original_path)"
						mode="aspectFit"
						class="detail-image"
						@click="previewImage(record.original_path)"
						@error="originalImageBroken = true"
					/>
					<view v-else class="detail-image image-broken">
						<AppIcon name="leaf" :size="48" color="#C3C9C3" />
						<text class="broken-text">原图加载失败</text>
					</view>
				</view>
				<view class="image-card">
					<text class="card-label">检测结果图</text>
					<image
						v-if="getFullUrl(record.result_path) && !resultImageBroken"
						:src="getFullUrl(record.result_path)"
						mode="aspectFit"
						class="detail-image"
						@click="previewImage(record.result_path)"
						@error="resultImageBroken = true"
					/>
					<view v-else class="detail-image image-broken">
						<AppIcon name="leaf" :size="48" color="#C3C9C3" />
						<text class="broken-text">结果图加载失败</text>
					</view>
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
							:class="{ healthy: item.class_name === '健康叶片' }"
						>{{ item.class_name }}</text>
						<text class="item-confidence">{{ (item.confidence * 100).toFixed(1) }}%</text>
					</view>
					<view class="confidence-bar">
						<view
							class="confidence-fill"
							:style="{ width: (item.confidence * 100) + '%' }"
							:class="{ healthy: item.class_name === '健康叶片' }"
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

		<EmptyState v-else-if="!loading" name="inbox" title="记录不存在" />
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { getHistoryDetail } from '@/api/history'
import { getFullUrl } from '@/utils/format'
import { showError } from '@/utils/error'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'
import DiseaseCard from '@/components/DiseaseCard.vue'
import AppIcon from '@/components/AppIcon.vue'

const loading = ref(true)
const record = ref(null)
const originalImageBroken = ref(false)
const resultImageBroken = ref(false)

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
		originalImageBroken.value = false
		resultImageBroken.value = false
	} catch (e) {
		showError(e, '加载失败')
	} finally {
		loading.value = false
		uni.stopPullDownRefresh()
	}
}

onPullDownRefresh(() => {
	loadRecord()
})

onMounted(() => {
	loadRecord()
})
</script>

<style lang="scss" scoped>
.history-detail-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.content {
	padding-bottom: 40rpx;
}

.image-section {
	padding: 24rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.image-card {
	background: var(--bg-1);
	border-radius: 20rpx;
	padding: 20rpx;
	border: 1rpx solid var(--border-light);
	box-shadow: 0 2rpx 12rpx rgba(31, 36, 33, 0.05);
}

.card-label {
	font-size: 26rpx;
	color: var(--text-3);
	margin-bottom: 12rpx;
	display: block;
}

.detail-image {
	display: block;
	width: 100%;
	height: 480rpx;
	border-radius: 12rpx;
	background: var(--bg-2);
}

.detail-image.image-broken {
	height: 480rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	gap: 16rpx;
	background: var(--bg-2);
}

.broken-text {
	font-size: 26rpx;
	color: var(--text-3);
}

.info-section {
	background: var(--bg-1);
	margin: 0 24rpx;
	border-radius: 20rpx;
	padding: 24rpx;
	border: 1rpx solid var(--border-light);
	box-shadow: 0 2rpx 12rpx rgba(31, 36, 33, 0.05);
}

.info-row {
	display: flex;
	justify-content: space-between;
	padding: 16rpx 0;
	border-bottom: 1rpx solid var(--border-light);
}

.info-row:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: var(--text-2);
}

.info-value {
	font-size: 28rpx;
	color: var(--text-1);
	font-weight: 500;
}

.detection-section {
	background: var(--bg-1);
	margin: 24rpx;
	border-radius: 20rpx;
	padding: 24rpx;
	border: 1rpx solid var(--border-light);
	box-shadow: 0 2rpx 12rpx rgba(31, 36, 33, 0.05);
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: var(--text-1);
	margin-bottom: 20rpx;
	display: block;
}

.detection-item {
	padding: 20rpx 0;
	border-bottom: 1rpx solid var(--border-light);
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
	background: var(--brand-glow);
	color: var(--brand);
	font-size: 24rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
}

.item-tag {
	font-size: 28rpx;
	font-weight: 600;
	color: var(--error);
	background: rgba(199, 62, 45, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.item-tag.healthy {
	color: var(--forest-2);
	background: var(--forest-light);
}

.item-confidence {
	margin-left: auto;
	font-size: 28rpx;
	font-weight: 600;
	color: var(--text-1);
}

.confidence-bar {
	height: 8rpx;
	background: var(--border-light);
	border-radius: 4rpx;
	overflow: hidden;
	margin-bottom: 20rpx;
}

.confidence-fill {
	height: 100%;
	border-radius: 4rpx;
	background: linear-gradient(90deg, var(--error) 0%, var(--warning) 50%, var(--brand) 100%);
	transition: width 0.5s ease;
}

.confidence-fill.healthy {
	background: var(--forest-2);
}
</style>
