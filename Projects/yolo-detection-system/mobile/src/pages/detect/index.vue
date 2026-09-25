<template>
	<view class="detect-page">
		<LoadingOverlay :visible="isDetecting" text="AI 正在分析中..." />

		<!-- 图片选择区域 -->
		<view v-if="!detectionResult" class="upload-section">
			<view class="upload-card" @click="showImageAction">
				<view v-if="imagePath" class="preview-area">
					<image :src="imagePath" mode="widthFix" class="preview-image" />
					<view class="reselect-btn" @click.stop="clearImage">
						<text class="reselect-icon">↻</text>
					</view>
				</view>
				<view v-else class="upload-placeholder">
					<text class="upload-icon">📷</text>
					<text class="upload-title">选择图片</text>
					<text class="upload-desc">支持拍照或从相册选择</text>
					<text class="upload-hint">图片大小不超过 5MB</text>
				</view>
			</view>

			<view class="action-area">
				<view class="save-toggle">
					<text class="toggle-label">保存到历史记录</text>
					<switch :checked="saveHistory" @change="saveHistory = !saveHistory" color="#E07A5F" />
				</view>
				<button
					class="detect-btn"
					:class="{ disabled: !imagePath || isDetecting }"
					:loading="isDetecting"
					@click="handleDetect"
				>
					<text>{{ isDetecting ? '检测中...' : '开始检测' }}</text>
				</button>
			</view>
		</view>

		<!-- 检测结果区域 -->
		<view v-else class="result-section">
			<!-- 结果图片 -->
			<view class="result-image-card">
				<text class="card-title">检测结果</text>
				<image :src="resultImageUrl" mode="widthFix" class="result-image" @click="previewResult" />
				<view class="image-stats">
					<text class="stat-item">检测目标: {{ detectionResult.total_count }}</text>
					<text class="stat-item">模型版本: {{ detectionResult.model_version }}</text>
				</view>
			</view>

			<!-- 检测列表 -->
			<view class="detection-list">
				<text class="list-title">检测结果列表</text>
				<view
					v-for="(item, index) in detectionResult.detections"
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

					<!-- 健康提示 -->
					<view v-if="item.class_name === '健康叶片'" class="healthy-box">
						<text class="healthy-icon">✅</text>
						<text class="healthy-text">该叶片未检测到病害特征，继续保持良好管理。</text>
					</view>

					<!-- 病害档案 -->
					<DiseaseCard
						v-else-if="item.disease_profile"
						:profile="item.disease_profile"
						:class-id="item.class_id"
					/>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="result-actions">
				<button class="action-btn ai-btn" @click="goToChat">
					<text class="btn-icon">💬</text>
					<text>咨询 AI</text>
				</button>
				<button class="action-btn reset-btn" @click="resetDetection">
					<text class="btn-icon">🔄</text>
					<text>重新检测</text>
				</button>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { detectImage } from '@/api/detect'
import { getFullUrl } from '@/utils/format'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import DiseaseCard from '@/components/DiseaseCard.vue'

const imagePath = ref('')
const saveHistory = ref(true)
const isDetecting = ref(false)
const detectionResult = ref(null)

const resultImageUrl = computed(() => {
	if (!detectionResult.value?.result_image) return ''
	return getFullUrl(detectionResult.value.result_image)
})

function showImageAction() {
	uni.showActionSheet({
		itemList: ['拍照', '从相册选择'],
		success: (res) => {
			const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
			chooseImage(sourceType)
		}
	})
}

function chooseImage(sourceType) {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType,
		success: (res) => {
			const tempPath = res.tempFilePaths[0]
			compressImage(tempPath)
		},
		fail: () => {
			uni.showToast({ title: '选择图片失败', icon: 'none' })
		}
	})
}

function compressImage(src) {
	uni.compressImage({
		src,
		quality: 60,
		success: (res) => {
			imagePath.value = res.tempFilePath
		},
		fail: () => {
			imagePath.value = src
		}
	})
}

function clearImage() {
	imagePath.value = ''
	detectionResult.value = null
}

async function handleDetect() {
	if (!imagePath.value || isDetecting.value) return

	isDetecting.value = true
	try {
		const result = await detectImage(imagePath.value, saveHistory.value)
		detectionResult.value = result
		uni.showToast({ title: '检测完成', icon: 'success' })
	} catch (e) {
		uni.showToast({ title: '检测失败，请重试', icon: 'none' })
	} finally {
		isDetecting.value = false
	}
}

function previewResult() {
	if (!resultImageUrl.value) return
	uni.previewImage({
		current: resultImageUrl.value,
		urls: [resultImageUrl.value]
	})
}

function goToChat() {
	if (!detectionResult.value) return
	uni.$emit('detect-to-chat', {
		result_image: resultImageUrl.value,
		detections: detectionResult.value.detections
	})
	uni.switchTab({ url: '/pages/chat/index' })
}

function resetDetection() {
	detectionResult.value = null
	imagePath.value = ''
}
</script>

<style lang="scss" scoped>
.detect-page {
	min-height: 100vh;
	padding: 24rpx;
	padding-bottom: 100rpx;
}

.upload-section {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.upload-card {
	background: #fff;
	border-radius: 24rpx;
	padding: 32rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.preview-area {
	position: relative;
	display: flex;
	justify-content: center;
}

.preview-image {
	max-width: 100%;
	border-radius: 16rpx;
}

.reselect-btn {
	position: absolute;
	top: 16rpx;
	right: 16rpx;
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	background: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: center;
	justify-content: center;
}

.reselect-icon {
	font-size: 32rpx;
	color: #fff;
}

.upload-placeholder {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 0;
}

.upload-icon {
	font-size: 100rpx;
	margin-bottom: 20rpx;
}

.upload-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 8rpx;
}

.upload-desc {
	font-size: 26rpx;
	color: #999;
	margin-bottom: 8rpx;
}

.upload-hint {
	font-size: 24rpx;
	color: #bbb;
}

.action-area {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.save-toggle {
	display: flex;
	align-items: center;
	justify-content: space-between;
	background: #fff;
	padding: 24rpx 28rpx;
	border-radius: 16rpx;
}

.toggle-label {
	font-size: 28rpx;
	color: #666;
}

.detect-btn {
	height: 96rpx;
	border-radius: 48rpx;
	background: linear-gradient(135deg, #E07A5F 0%, #C96247 100%);
	color: #fff;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
}

.detect-btn.disabled {
	opacity: 0.5;
}

.detect-btn::after {
	border: none;
}

.result-section {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.result-image-card {
	background: #fff;
	border-radius: 24rpx;
	padding: 28rpx;
}

.card-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.result-image {
	width: 100%;
	border-radius: 16rpx;
}

.image-stats {
	display: flex;
	gap: 32rpx;
	margin-top: 16rpx;
	padding-top: 16rpx;
	border-top: 1rpx solid #f0f0f0;
}

.stat-item {
	font-size: 24rpx;
	color: #999;
}

.detection-list {
	background: #fff;
	border-radius: 24rpx;
	padding: 28rpx;
}

.list-title {
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

.healthy-box {
	display: flex;
	gap: 12rpx;
	margin-top: 16rpx;
	padding: 20rpx;
	background: rgba(224, 122, 95, 0.08);
	border-radius: 16rpx;
}

.healthy-icon {
	font-size: 32rpx;
	flex-shrink: 0;
}

.healthy-text {
	font-size: 26rpx;
	color: #333;
	line-height: 1.5;
}

.result-actions {
	display: flex;
	gap: 20rpx;
	padding-bottom: 40rpx;
}

.action-btn {
	flex: 1;
	height: 88rpx;
	border-radius: 44rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8rpx;
	font-size: 28rpx;
	font-weight: 600;
}

.action-btn::after {
	border: none;
}

.ai-btn {
	background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
	color: #fff;
}

.reset-btn {
	background: #fff;
	color: #666;
	border: 2rpx solid #eee;
}

.btn-icon {
	font-size: 28rpx;
}
</style>
