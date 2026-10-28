<template>
	<view class="detect-page">
		<LoadingOverlay :visible="isDetecting" text="AI 正在分析中..." />

		<!-- 图片选择区域 -->
		<view v-if="!detectionResult" class="upload-section">
			<view class="section-head">
				<text class="section-eyebrow">STEP 01</text>
				<text class="section-title">上传叶片照片</text>
				<text class="section-desc">优先选择清晰、单叶、正对镜头的照片</text>
			</view>

			<view class="upload-card" @click="showImageAction">
				<view v-if="imagePath" class="preview-area">
					<image :src="imagePath" mode="aspectFit" class="preview-image" />
					<view class="image-meta">
						<text class="image-meta-text">已选择叶片照片</text>
						<text class="image-meta-action">点击更换</text>
					</view>
					<view class="reselect-btn" @click.stop="clearImage">
						<AppIcon name="close" :size="28" color="#FFFFFF" />
					</view>
				</view>
				<view v-else class="upload-placeholder">
					<view class="upload-icon-wrap">
						<AppIcon class="upload-icon" name="camera" :size="72" color="#C8442F" />
					</view>
					<text class="upload-title">拍照或选择图片</text>
					<text class="upload-desc">支持压缩后上传，适合日常田间记录</text>
					<view class="upload-actions">
						<view class="upload-action-btn">
							<AppIcon name="camera" :size="26" color="#1E3B2C" />
							<text class="upload-action-text">拍照</text>
						</view>
						<view class="upload-action-btn">
							<AppIcon name="image" :size="26" color="#1E3B2C" />
							<text class="upload-action-text">相册</text>
						</view>
					</view>
				</view>
			</view>

			<view class="action-area">
				<view class="save-toggle">
					<view class="toggle-text">
						<text class="toggle-label">保存到历史记录</text>
						<text class="toggle-desc">方便后续查看和追踪</text>
					</view>
					<switch :checked="saveHistory" @change="saveHistory = !saveHistory" color="#C8442F" />
				</view>
				<button
					class="detect-btn"
					:class="{ disabled: !imagePath || isDetecting }"
					:loading="isDetecting"
					@click="handleDetect"
				>
					<AppIcon v-if="imagePath" name="scan" :size="32" color="#FFFFFF" />
					<text>{{ isDetecting ? '检测中...' : '开始检测' }}</text>
				</button>
			</view>
		</view>

		<!-- 检测结果区域 -->
		<view v-else class="result-section">
			<view class="result-head">
				<text class="section-eyebrow">STEP 02</text>
				<text class="section-title">检测结果</text>
				<text class="section-desc">共识别 {{ detectionResult.total_count }} 个目标，模型 {{ detectionResult.model_version }}</text>
			</view>

			<!-- 低置信度提示 -->
			<view v-if="lowConfidence" class="low-confidence-card">
				<view class="low-confidence-head">
					<AppIcon name="alert" :size="32" color="#D9A11E" />
					<text class="low-confidence-title">
						检测置信度偏低（阈值 {{ formatPercent(lowConfidence.threshold) }}），建议重新拍摄清晰叶片照片
					</text>
				</view>
				<view v-if="lowConfidence.candidates.length" class="candidate-row">
					<text class="candidate-label">可能：</text>
					<view
						v-for="candidate in lowConfidence.candidates"
						:key="candidate.class_id ?? candidate.class_name"
						class="candidate-tag"
					>
						<text>{{ candidate.class_name }}({{ Math.round((candidate.confidence || 0) * 100) }}%)</text>
					</view>
				</view>
				<text v-if="lowConfidence.samplePoolId" class="low-confidence-note">
					该图片已自动收录至样本池待人工复核
				</text>
			</view>

			<!-- 结果图片 -->
			<view class="result-image-card">
				<view class="card-head">
					<view class="card-title-row">
						<text class="card-title">标注结果</text>
						<text class="card-count">{{ detectionResult.detections.length }} 个目标</text>
					</view>
					<text class="preview-link" @click="previewResult">查看大图</text>
				</view>
				<image
					v-if="resultImageUrl && !resultImageBroken"
					:src="resultImageUrl"
					mode="aspectFit"
					class="result-image"
					@click="previewResult"
					@error="onResultImageError"
				/>
				<view v-else class="result-image image-broken">
					<AppIcon name="alert" :size="48" color="#8A938C" />
					<text class="broken-text">结果图加载失败</text>
				</view>
				<view class="image-stats">
					<text class="stat-item">检测目标 {{ detectionResult.total_count }}</text>
					<text class="stat-divider"></text>
					<text class="stat-item">模型 v{{ detectionResult.model_version }}</text>
				</view>
			</view>

			<!-- 检测列表 -->
			<view class="detection-list">
				<view class="card-head">
					<view class="card-title-row">
						<text class="card-title">识别明细</text>
						<text class="card-count">按置信度排序</text>
					</view>
				</view>
				<view
					v-for="(item, index) in detectionResult.detections"
					:key="index"
					class="detection-item"
				>
					<view class="item-header">
						<view class="item-index" :class="{ healthy: item.class_name === '健康叶片' }">
							<text>{{ index + 1 }}</text>
						</view>
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
						<AppIcon name="check-circle" :size="32" color="#3C7A52" />
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
					<AppIcon name="chat" :size="30" color="#FFFFFF" />
					<text>咨询 AI</text>
				</button>
				<button class="action-btn reset-btn" @click="resetDetection">
					<AppIcon name="refresh" :size="30" color="#1E3B2C" />
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
import { showError } from '@/utils/error'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import DiseaseCard from '@/components/DiseaseCard.vue'
import AppIcon from '@/components/AppIcon.vue'
import { useChatStore } from '@/store/chat'

const chatStore = useChatStore()

const imagePath = ref('')
const saveHistory = ref(true)
const isDetecting = ref(false)
const detectionResult = ref(null)
const resultImageBroken = ref(false)

const resultImageUrl = computed(() => {
	if (!detectionResult.value?.result_image) return ''
	return getFullUrl(detectionResult.value.result_image)
})

const lowConfidence = computed(() => {
	const result = detectionResult.value
	if (!result || result.low_confidence !== true) return null
	return {
		threshold: typeof result.confidence_threshold === 'number' ? result.confidence_threshold : 0.5,
		candidates: Array.isArray(result.top_candidates)
			? result.top_candidates.filter((item) => item && item.class_name)
			: [],
		samplePoolId: result.sample_pool_id ?? null
	}
})

function formatPercent(value) {
	return typeof value === 'number' ? `${Math.round(value * 100)}%` : '-'
}

function onResultImageError() {
	resultImageBroken.value = true
}

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
		resultImageBroken.value = false
		uni.showToast({ title: '检测完成', icon: 'success' })
	} catch (e) {
		showError(e, '检测失败，请重试')
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
	chatStore.setPendingDetection({
		result_image: resultImageUrl.value,
		detections: detectionResult.value.detections
	})
	uni.switchTab({ url: '/pages/chat/index' })
}

function resetDetection() {
	detectionResult.value = null
	imagePath.value = ''
	resultImageBroken.value = false
}
</script>

<style lang="scss" scoped>
.detect-page {
	min-height: 100vh;
	padding: 24rpx;
	padding-bottom: 100rpx;
	background: var(--bg-2);
}

.upload-section,
.result-section {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.section-head,
.result-head {
	display: flex;
	flex-direction: column;
	gap: 6rpx;
	padding: 8rpx 8rpx 0;
}

.section-eyebrow {
	font-size: 20rpx;
	font-weight: 700;
	color: var(--brand);
	letter-spacing: 4rpx;
}

.section-title {
	font-size: 40rpx;
	font-weight: 700;
	color: var(--text-1);
	line-height: 1.25;
}

.section-desc {
	font-size: 24rpx;
	color: var(--text-3);
	line-height: 1.5;
}

.upload-card {
	background: var(--bg-1);
	border-radius: 24rpx;
	padding: 24rpx;
	border: 1rpx solid var(--border-light);
	box-shadow: var(--shadow-sm);
}

.preview-area {
	position: relative;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	border-radius: 20rpx;
	background: var(--bg-2);
}

.preview-image {
	display: block;
	width: 100%;
	height: 560rpx;
	background: var(--bg-2);
}

.image-meta {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 18rpx 22rpx;
	background: var(--forest);
}

.image-meta-text {
	font-size: 24rpx;
	font-weight: 600;
	color: #FFFFFF;
}

.image-meta-action {
	font-size: 23rpx;
	color: #8FBF9F;
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

.upload-placeholder {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 48rpx 24rpx;
}

.upload-icon-wrap {
	width: 128rpx;
	height: 128rpx;
	border-radius: 40rpx;
	background: var(--brand-glow);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 24rpx;
}

.upload-icon {
	display: block;
}

.upload-title {
	font-size: 32rpx;
	font-weight: 700;
	color: var(--text-1);
	margin-bottom: 10rpx;
}

.upload-desc {
	font-size: 25rpx;
	color: var(--text-3);
	line-height: 1.6;
	margin-bottom: 24rpx;
	text-align: center;
}

.upload-actions {
	display: flex;
	gap: 16rpx;
}

.upload-action-btn {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 16rpx 28rpx;
	border-radius: 999rpx;
	background: var(--forest-light);
	border: 1rpx solid rgba(44, 87, 64, 0.16);
}

.upload-action-text {
	font-size: 24rpx;
	font-weight: 600;
	color: var(--forest);
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
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	padding: 22rpx 28rpx;
	border-radius: 20rpx;
}

.toggle-text {
	display: flex;
	flex-direction: column;
	gap: 6rpx;
}

.toggle-label {
	font-size: 28rpx;
	font-weight: 600;
	color: var(--text-1);
}

.toggle-desc {
	font-size: 23rpx;
	color: var(--text-3);
}

.detect-btn {
	height: 96rpx;
	border-radius: 24rpx;
	background: var(--brand);
	box-shadow: var(--shadow-brand);
	color: #fff;
	font-size: 32rpx;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12rpx;
}

.detect-btn.disabled {
	opacity: 0.5;
	box-shadow: none;
}

.detect-btn::after {
	border: none;
}

.result-image-card,
.detection-list {
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 24rpx;
	padding: 28rpx;
	box-shadow: var(--shadow-sm);
}

.low-confidence-card {
	display: flex;
	flex-direction: column;
	gap: 14rpx;
	padding: 24rpx;
	border-radius: 20rpx;
	background: rgba(217, 161, 30, 0.12);
	border: 1rpx solid rgba(217, 161, 30, 0.32);
}

.low-confidence-head {
	display: flex;
	align-items: flex-start;
	gap: 12rpx;
}

.low-confidence-title {
	flex: 1;
	font-size: 25rpx;
	line-height: 1.6;
	font-weight: 600;
	color: var(--text-1);
}

.candidate-row {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 10rpx;
	padding-left: 44rpx;
}

.candidate-label {
	font-size: 23rpx;
	color: var(--text-2);
}

.candidate-tag {
	padding: 4rpx 12rpx;
	border-radius: 10rpx;
	background: rgba(217, 161, 30, 0.18);
}

.candidate-tag text {
	font-size: 22rpx;
	color: #8A6410;
}

.low-confidence-note {
	padding-left: 44rpx;
	font-size: 23rpx;
	line-height: 1.5;
	color: var(--text-2);
}

.card-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20rpx;
}

.card-title-row {
	display: flex;
	align-items: baseline;
	gap: 12rpx;
}

.card-title {
	font-size: 32rpx;
	font-weight: 700;
	color: var(--text-1);
}

.card-count {
	font-size: 22rpx;
	color: var(--text-3);
}

.preview-link {
	font-size: 24rpx;
	font-weight: 600;
	color: var(--brand);
}

.result-image {
	display: block;
	width: 100%;
	height: 560rpx;
	border-radius: 16rpx;
	background: var(--bg-2);
}

.result-image.image-broken {
	height: 560rpx;
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

.image-stats {
	display: flex;
	align-items: center;
	gap: 24rpx;
	margin-top: 16rpx;
	padding: 18rpx 20rpx;
	border-radius: 16rpx;
	background: var(--forest-light);
}

.stat-item {
	font-size: 24rpx;
	font-weight: 600;
	color: var(--forest);
}

.stat-divider {
	width: 1rpx;
	height: 28rpx;
	background: rgba(44, 87, 64, 0.2);
}

.detection-item {
	padding: 24rpx 0;
	border-bottom: 1rpx solid var(--border-light);
}

.detection-item:last-child {
	border-bottom: none;
}

.item-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 14rpx;
}

.item-index {
	width: 40rpx;
	height: 40rpx;
	border-radius: 14rpx;
	background: var(--brand-glow);
	color: var(--brand);
	font-size: 24rpx;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
}

.item-index.healthy {
	background: var(--forest-light);
	color: var(--success);
}

.item-tag {
	font-size: 28rpx;
	font-weight: 700;
	color: var(--brand);
	background: var(--brand-glow);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.item-tag.healthy {
	color: var(--success);
	background: var(--forest-light);
}

.item-confidence {
	margin-left: auto;
	font-size: 28rpx;
	font-weight: 700;
	color: var(--text-1);
}

.confidence-bar {
	height: 10rpx;
	background: var(--bg-3);
	border-radius: 5rpx;
	overflow: hidden;
}

.confidence-fill {
	height: 100%;
	border-radius: 5rpx;
	background: linear-gradient(90deg, var(--brand-dark) 0%, var(--brand) 60%, var(--brand-light) 100%);
	transition: width 0.5s ease;
}

.confidence-fill.healthy {
	background: linear-gradient(90deg, #2C5740 0%, var(--success) 100%);
}

.healthy-box {
	display: flex;
	gap: 12rpx;
	margin-top: 18rpx;
	padding: 20rpx;
	background: var(--forest-light);
	border-radius: 16rpx;
}

.healthy-text {
	font-size: 26rpx;
	color: var(--text-1);
	line-height: 1.6;
}

.result-actions {
	display: flex;
	gap: 20rpx;
	padding-bottom: 40rpx;
}

.action-btn {
	flex: 1;
	height: 88rpx;
	border-radius: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8rpx;
	font-size: 28rpx;
	font-weight: 700;
}

.action-btn::after {
	border: none;
}

.ai-btn {
	background: var(--brand);
	box-shadow: var(--shadow-brand);
	color: #FFFFFF;
}

.reset-btn {
	background: var(--bg-1);
	color: var(--text-2);
	border: 1rpx solid var(--border);
}
</style>
