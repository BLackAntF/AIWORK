<template>
	<view class="empty-state">
		<text class="empty-icon">{{ icon }}</text>
		<text class="empty-title">{{ title }}</text>
		<text class="empty-desc">{{ desc }}</text>
		<slot></slot>
	</view>
</template>

<script setup>
defineProps({
	icon: { type: String, default: '📭' },
	title: { type: String, default: '暂无数据' },
	desc: { type: String, default: '' }
})
</script>

<style lang="scss" scoped>
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 80rpx 40rpx;
}

.empty-icon {
	font-size: 120rpx;
	margin-bottom: 24rpx;
	opacity: 0.6;
}

.empty-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #666;
	margin-bottom: 12rpx;
}

.empty-desc {
	font-size: 26rpx;
	color: #999;
}
</style>
