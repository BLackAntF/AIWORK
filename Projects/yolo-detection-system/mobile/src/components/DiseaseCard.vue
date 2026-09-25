<template>
	<view class="disease-card" @click="goDetail">
		<view class="card-header">
			<view class="disease-tag">
				<text class="tag-icon">📋</text>
				<text class="tag-text">{{ profile.disease_name }}</text>
			</view>
			<text class="card-arrow">›</text>
		</view>

		<view class="card-body">
			<view class="info-item">
				<text class="info-label">诱因</text>
				<text class="info-value">{{ profile.causes }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">典型症状</text>
				<text class="info-value">{{ profile.symptoms }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">防治方案</text>
				<text class="info-value">{{ profile.treatment }}</text>
			</view>

			<view v-if="profile.pesticides" class="pesticides-row">
				<text class="pesticides-label">推荐药剂</text>
				<view class="pesticides-tags">
					<text
						v-for="(pesticide, idx) in pesticideList"
						:key="idx"
						class="pesticide-tag"
					>{{ pesticide }}</text>
				</view>
			</view>
		</view>

		<view class="card-footer">
			<text class="footer-text">点击查看完整档案</text>
		</view>
	</view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	profile: { type: Object, required: true },
	classId: { type: [Number, String], default: '' }
})

const pesticideList = computed(() => {
	if (!props.profile.pesticides) return []
	return props.profile.pesticides.split(/[,，、]/).filter(p => p.trim())
})

function goDetail() {
	if (props.classId) {
		uni.navigateTo({ url: `/pages/archive/detail?id=${props.classId}` })
	}
}
</script>

<style lang="scss" scoped>
.disease-card {
	background: #fff;
	border-radius: 20rpx;
	padding: 28rpx;
	margin-top: 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.card-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20rpx;
	padding-bottom: 16rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.disease-tag {
	display: flex;
	align-items: center;
	gap: 8rpx;
	background: rgba(224, 122, 95, 0.1);
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
}

.tag-icon {
	font-size: 28rpx;
}

.tag-text {
	font-size: 28rpx;
	font-weight: 600;
	color: #E07A5F;
}

.card-arrow {
	font-size: 40rpx;
	color: #ccc;
}

.card-body {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.info-item {
	display: flex;
	gap: 16rpx;
}

.info-label {
	flex-shrink: 0;
	width: 100rpx;
	font-size: 26rpx;
	color: #999;
	font-weight: 500;
}

.info-value {
	flex: 1;
	font-size: 26rpx;
	color: #333;
	line-height: 1.5;
}

.pesticides-row {
	margin-top: 8rpx;
}

.pesticides-label {
	font-size: 26rpx;
	color: #999;
	font-weight: 500;
	margin-bottom: 12rpx;
	display: block;
}

.pesticides-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.pesticide-tag {
	background: rgba(255, 152, 0, 0.15);
	color: #FF9800;
	font-size: 24rpx;
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.card-footer {
	margin-top: 16rpx;
	padding-top: 16rpx;
	border-top: 1rpx solid #f0f0f0;
}

.footer-text {
	font-size: 24rpx;
	color: #999;
}
</style>
