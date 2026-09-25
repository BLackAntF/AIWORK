<template>
	<view class="page-header">
		<view v-if="showBack" class="back-btn" @click="handleBack">
			<text class="back-icon">‹</text>
		</view>

		<view class="header-main">
			<text class="header-title">{{ title }}</text>
			<text v-if="subtitle" class="header-subtitle">{{ subtitle }}</text>
		</view>

		<view class="header-actions">
			<slot name="actions"></slot>
		</view>
	</view>
</template>

<script setup>
defineProps({
	title: { type: String, default: '' },
	subtitle: { type: String, default: '' },
	showBack: { type: Boolean, default: false }
})

function handleBack() {
	const pages = getCurrentPages()
	if (pages.length > 1) {
		uni.navigateBack()
	} else {
		uni.switchTab({ url: '/pages/index/index' })
	}
}
</script>

<style lang="scss" scoped>
.page-header {
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: 28rpx 32rpx;
	background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
}

.back-btn {
	width: 56rpx;
	height: 56rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.back-icon {
	font-size: 52rpx;
	line-height: 1;
	color: #FFFFFF;
}

.header-main {
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #FFFFFF;
}

.header-subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.85);
	margin-top: 4rpx;
}

.header-actions {
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: flex-end;
	gap: 16rpx;
}
</style>