<template>
	<view class="page-header">
		<view class="header-grid"></view>
		<view v-if="showBack" class="back-btn" @click="handleBack">
			<text class="back-icon">‹</text>
		</view>

		<view class="header-main">
			<text class="header-eyebrow">{{ eyebrow }}</text>
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
	eyebrow: { type: String, default: '' },
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
	position: relative;
	overflow: hidden;
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: calc(var(--status-bar-height, 0px) + 24rpx) 32rpx 28rpx;
	background: var(--forest);
}

.header-grid {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 100%;
	background-image:
		linear-gradient(rgba(255, 255, 255, 0.045) 1rpx, transparent 1rpx),
		linear-gradient(90deg, rgba(255, 255, 255, 0.045) 1rpx, transparent 1rpx);
	background-size: 44rpx 44rpx;
	pointer-events: none;
}

.back-btn {
	position: relative;
	width: 56rpx;
	height: 56rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	border-radius: 16rpx;
	background: rgba(255, 255, 255, 0.1);
	border: 1rpx solid rgba(255, 255, 255, 0.14);
}

.back-icon {
	font-size: 44rpx;
	line-height: 1;
	color: #FFFFFF;
}

.header-main {
	position: relative;
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.header-eyebrow {
	font-size: 18rpx;
	color: #8FBF9F;
	letter-spacing: 3rpx;
	margin-bottom: 6rpx;
	text-transform: uppercase;
}

.header-title {
	font-size: 34rpx;
	font-weight: 700;
	color: #FFFFFF;
	line-height: 1.25;
}

.header-subtitle {
	font-size: 23rpx;
	color: rgba(255, 255, 255, 0.78);
	margin-top: 6rpx;
	line-height: 1.5;
}

.header-actions {
	position: relative;
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: flex-end;
	gap: 16rpx;
}
</style>