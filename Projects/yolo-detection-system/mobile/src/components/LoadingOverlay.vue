<template>
	<view v-if="visible" class="loading-overlay">
		<view class="loading-content">
			<view class="loading-spinner"></view>
			<text class="loading-text">{{ text }}</text>
		</view>
	</view>
</template>

<script setup>
defineProps({
	visible: { type: Boolean, default: false },
	text: { type: String, default: '加载中...' }
})
</script>

<style lang="scss" scoped>
.loading-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
}

.loading-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 20rpx;
	background: #fff;
	padding: 48rpx 64rpx;
	border-radius: 24rpx;
}

.loading-spinner {
	width: 64rpx;
	height: 64rpx;
	border: 4rpx solid #eee;
	border-top-color: #E07A5F;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}

.loading-text {
	font-size: 28rpx;
	color: #666;
}
</style>
